FROM --platform=linux/amd64 python:3.9-slim-buster

RUN apt-get update
RUN apt-get install -y xvfb vim wget unzip
RUN wget -N https://chromedriver.storage.googleapis.com/100.0.4896.60/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN mv chromedriver /usr/local/bin/chromedriver
RUN wget -N https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb
RUN groupadd -g 1000 user_default
RUN useradd -g 1000 -u 1000 -m user_default
#RUN pip install discord selenium beautifulsoup4 pandas pyvirtualdisplay
COPY ./share/ /home/user_default/
RUN python3 -m pip install -r /home/user_default/requirements.txt
USER 1000
WORKDIR /home/user_default/

ENTRYPOINT [ "python" ]
CMD ["-m", "korailbot"]
