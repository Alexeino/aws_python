import boto3
import tempfile
from PIL import Image
import os
import io
import math
import sys

s3 = boto3.client("s3")
tile_size = 100
SOURCE_BUCKET = "gridsourcebucket"
DESTINATION_BUCKET = "griddestinationbucket"

def grid_maker(src_bucket,dst_bucket,tile_size):
    resp = s3.list_objects_v2(Bucket=src_bucket)
    source_images = [obj["Key"] for obj in resp["Contents"]]
    image_count = len(source_images)

    tiles_width = math.floor(math.sqrt(image_count))
    tiles_height = math.ceil(image_count/tiles_width)
    
    print(f"Converting: {image_count} source images. Creating: {tiles_width} X {tiles_height} grid.")

    destination_image = Image.new(mode="RGB",size=(
        tiles_width * tile_size, tiles_height * tile_size
    ))
    
    for y in range(tiles_height):
        for x in range(tiles_width):
            if source_images:
                filename = source_images.pop()
                response = s3.get_object(Bucket=src_bucket,Key=filename)

                image_data = response['Body'].read()
                
                img = Image.open(io.BytesIO(image_data))
                img_width = img.size[0]
                img_height = img.size[1]

                crop_square = min(img.size)
                img = img.crop(((img_width - crop_square)//2,
                                (img_height - crop_square) // 2,
                                (img_width + crop_square)//2,
                                (img_height+crop_square)//2
                                ))
                
                img = img.resize((tile_size,tile_size))

                destination_image.paste(img,(x*tile_size,y*tile_size))

    temp_file = tempfile.NamedTemporaryFile(suffix=".jpg").name
    destination_image.save(temp_file)
    print(f"Creating temp file {temp_file}")
    
    destination_key = os.urandom(16).hex() + ".jpg"
    with open(temp_file,"rb") as data:
        s3.put_object(
            Bucket = dst_bucket,
            Key = destination_key,
            Body = data,
            ContentType = "image/jpg"
        )
        
    print(f"Saved file to s3 bucket: {dst_bucket}, key:{destination_key}")

    presigned_url = s3.generate_presigned_url("get_object",Params={
        "Bucket":dst_bucket,"Key":destination_key
    },ExpiresIn=5 * 60)
    
    print(f"Presigned URL: {presigned_url}")
    return presigned_url

def lambda_handler(event,context):
    source_bucket = event["SOURCE_BUCKET"]
    destination_bucket = event["DESTINATION_BUCKET"]
    
    return grid_maker(source_bucket,destination_bucket,tile_size=100)
