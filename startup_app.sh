#!/bin/sh
# startup-app.sh

echo "SLEEPING UNTIL COMPLETE"
sleep 20
echo "POPULATING ELASTIC SEARCH"
python populate_elasticsearch.py
echo "DONE! launching uvicorn"
exec uvicorn main:app --host 0.0.0.0 --port 8000
