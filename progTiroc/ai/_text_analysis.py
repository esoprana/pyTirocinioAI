import json
import os

import dialogflow_v2 as dialogflow
import google.cloud.language

from google.protobuf.json_format import MessageToDict

from google.oauth2 import service_account

credential = service_account.Credentials.from_service_account_info(
    json.loads(os.environ['GOOGLE_APPLICATION_CREDENTIALS_RAW']))


def analyze_intent(project_id, session_id, text: str, language_code, log):
    """Returns the result of detect intent with texts as inputs.

    Using the same `session_id` between requests allows continuation
    of the conversaion."""
    session_client = dialogflow.SessionsClient(credentials=credential)

    session = session_client.session_path(project_id, session_id)
    log.info('Session path: {}\n'.format(session))

    text_input = dialogflow.types.TextInput(
        text=text, language_code=language_code)

    query_input = dialogflow.types.QueryInput(text=text_input)

    response = session_client.detect_intent(
        session=session, query_input=query_input)

    response.query_result.intent.name = response.query_result.intent.name[
        len('projects/') + len(project_id) + len('/agent/intents/'):]

    return MessageToDict(response.query_result)


def analyze_categories(text: str, log) -> list:
    client = google.cloud.language.LanguageServiceClient(credentials=credential)

    document = google.cloud.language.types.Document(
        content=text,
        type=google.cloud.language.enums.Document.Type.PLAIN_TEXT,
    )

    try:
        response = client.classify_text(document=document).categories
    except Exception as ex:
        log.critical(ex)
        response = []

    return [] if not response else MessageToDict(response)


def analyze_sentiment(text: str, log) -> dict:
    client = google.cloud.language.LanguageServiceClient(credentials=credential)
    document = google.cloud.language.types.Document(
        content=text,
        type=google.cloud.language.enums.Document.Type.PLAIN_TEXT,
    )

    try:
        sentiment = client.analyze_sentiment(
            document=document,
            encoding_type='UTF32',
        ).document_sentiment
    except Exception as ex:
        print(ex)
        sentiment = {'score': 0.0, 'magnitude': 0.0}

    return MessageToDict(sentiment)
