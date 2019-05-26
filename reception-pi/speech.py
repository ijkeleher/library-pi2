#!/usr/bin/env python3

# Reference: https://pypi.org/project/SpeechRecognition/
# Reference: https://www.geeksforgeeks.org/speech-recognition-in-python-using-google-speech-api/
# Reference: Code From Week 10 Tutorial

import subprocess
import speech_recognition as sr


class Speech2Text:
    """
    voice function which convert voice into text
    """
    # MIC_NAME = "Microsoft® LifeCam HD-3000: USB Audio (hw:2,0)" # laptop
    # config
    # raspberry pi config
    MIC_NAME = "Microsoft® LifeCam HD-3000: USB Audio (hw:1,0)"

    def record(self):
        """
        record voice

        Return:
            book name according to voice
        except:
            WaitTimeError

            UnKnownValueError

            RequestError
        """
        # Set the device ID of the mic that we specifically want to use to
        # avoid ambiguity
        for i, microphone_name in enumerate(
                sr.Microphone.list_microphone_names()):
            print(microphone_name)
            if microphone_name == self.MIC_NAME:
                device_id = i
                break

        # obtain audio from the microphone
        recognize = sr.Recognizer()
        with sr.Microphone(device_index=device_id) as source:
            # clear console of errors
            subprocess.run("clear")

            # wait for a second to let the recognizer adjust the
            # energy threshold based on the surrounding noise level
            recognize.adjust_for_ambient_noise(source)

            print("Say something!")
            try:
                audio = recognize.listen(source, timeout=1.5)
            except sr.WaitTimeoutError:
                print("Listening timed out whilst waiting for phrase to start")
                quit()

        print("Finished listening, analyzing")
        # recognize speech using Google Speech Recognition
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            print(
                "Google Speech Recognition thinks you said '{}'".format(
                    recognize.recognize_google(audio)))
            book_name = recognize.recognize_google(audio)
            return book_name
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as error:
            print(
                "Could not request results from Google Speech Recognition service; {0}".format(error))
