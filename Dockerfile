FROM python:3.11

WORKDIR /english_bot

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    python3-venv \
 && rm -rf /var/lib/apt/lists/*

RUN python -m venv venv
RUN . venv/bin/activate
ENV PATH="/english_bot/venv/bin:$PATH"
ENV PYTHONPATH="$PYTHONPATH:/english_bot/app"


RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Command to run the application
CMD ["python", "app/bot.py"]

