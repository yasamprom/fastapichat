FROM python:3.9
RUN mkdir /app
WORKDIR /app
COPY . .
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/app/fastapichat"
CMD ["uvicorn", "fastapichat.main:app", "--reload"]