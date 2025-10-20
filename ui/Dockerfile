FROM python:3.11-slim

WORKDIR /usr/src/ui

COPY ./ui ./ui

RUN pip install --upgrade pip
RUN pip install streamlit pandas numpy python-dotenv

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]