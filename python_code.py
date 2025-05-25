def listSpeechSynthesisTasks(request):
    request = before_client_execution(request)
    return execute_list_speech_synthesis_tasks(request)