import json
import boto3
import traceback

bedrock_client = boto3.client(service_name='bedrock-runtime')

def generate_conversation(model_id, messages):
    response = bedrock_client.converse(
        modelId=model_id,
        messages=messages,
        inferenceConfig={"temperature": 0.5, "maxTokens": 2000, "topP": 0.6}
    )
    return response

def lambda_handler(event, context):
    model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    messages = []

    try:
        body = json.loads(event['body'])
        question = body['message']

        message = {
            "role": "user",
            "content": [{"text": question}]
        }
        messages.append(message)

        response = generate_conversation(model_id, messages)

        output_message = response['output']['message']['content'][0]['text']
        messages.append({
            "role": "assistant",
            "content": [{"text": output_message}]
        })

        print("Role: user")
        print(f"\tQuestion: {question}")
        print("Role: assistant")
        print(f"\tResponse: {output_message}\n")

        response_dict = {
            'question': question,
            'answer': output_message
        }

        json_response = json.dumps(response_dict, ensure_ascii=False)

        return {
            'statusCode': 200,
            'body': json_response,
            'headers': {
                'Content-Type': 'application/json; charset=utf-8'
            }
        }
    except KeyError as e:
        error_msg = f"Missing key in event: {str(e)}"
        print(error_msg)
        return {
            'statusCode': 400,
            'body': json.dumps({'error': error_msg}, ensure_ascii=False),
            'headers': {
                'Content-Type': 'application/json; charset=utf-8'
            }
        }
    except json.JSONDecodeError as e:
        error_msg = f"Error decoding JSON: {str(e)}"
        print(error_msg)
        return {
            'statusCode': 400,
            'body': json.dumps({'error': error_msg}, ensure_ascii=False),
            'headers': {
                'Content-Type': 'application/json; charset=utf-8'
            }
        }
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps({'error': error_msg, 'trace': traceback.format_exc()}, ensure_ascii=False),
            'headers': {
                'Content-Type': 'application/json; charset=utf-8'
            }
        }
