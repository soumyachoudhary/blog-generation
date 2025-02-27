import boto3
import botocore.config
import json
from datetime import datetime

def generate_blog_using_bedrock(topic: str) -> str:
    """
    Generates a blog using Amazon Bedrock based on the given topic.
    """
    prompt = f"""<s>[INST]Human: Write a 200-word blog on the topic {topic}
    Assistant:[/INST]
    """
    
    request_payload = {
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
        "top_p": 0.9
    }
    
    try:
        bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1",
                                     config=botocore.config.Config(read_timeout=300, retries={'max_attempts': 3}))
        response = bedrock_client.invoke_model(
            body=json.dumps(request_payload),
            modelId="meta.llama2-13b-chat-v1"
        )
        
        response_content = response.get('body').read()
        response_data = json.loads(response_content)
        return response_data.get('generation', '')
    except Exception as error:
        print(f"Error generating the blog: {error}")
        return ""

def save_to_s3(bucket_name: str, file_key: str, content: str):
    """
    Saves the generated blog content to an S3 bucket.
    """
    s3_client = boto3.client('s3')
    try:
        s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=content)
        print("Blog saved to S3 successfully.")
    except Exception as error:
        print(f"Error saving blog to S3: {error}")

def lambda_handler(event, context):
    """
    AWS Lambda handler function to generate a blog and save it to S3.
    """
    try:
        request_data = json.loads(event.get('body', '{}'))
        blog_topic = request_data.get('blog_topic', '')
        
        if not blog_topic:
            return {'statusCode': 400, 'body': json.dumps('Invalid request: Missing blog topic')}
        
        generated_blog = generate_blog_using_bedrock(blog_topic)
        
        if generated_blog:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            s3_file_key = f"blog-output/{timestamp}.txt"
            s3_bucket = 'aws_bedrock_course1'
            save_to_s3(s3_bucket, s3_file_key, generated_blog)
            return {'statusCode': 200, 'body': json.dumps('Blog generation and upload completed.')}
        else:
            return {'statusCode': 500, 'body': json.dumps('Blog generation failed.')}
    except Exception as error:
        print(f"Error processing request: {error}")
        return {'statusCode': 500, 'body': json.dumps('Internal server error.')}
\  
