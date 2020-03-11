# 5x5 with k = 4, g = 1; once move first and once move second.
# move first
python3 AI_runner.py 5 5 4 1 l ../src/connect-k-python/main.py SampleAIs/AverageAI_v2.pyc
echo "player 1 should win"
# move second
python3 AI_runner.py 5 5 4 1 l SampleAIs/AverageAI_v2.pyc ../src/connect-k-python/main.py
echo "player 2 should win"


# 7x7 with k = 5, g = 1; once move first and once move second.
# move first
python3 AI_runner.py 7 7 5 1 l ../src/connect-k-python/main.py SampleAIs/AverageAI_v2.pyc
echo "player 1 should win"
# move second
python3 AI_runner.py 7 7 5 1 l SampleAIs/AverageAI_v2.pyc ../src/connect-k-python/main.py
echo "player 2 should win"


# 5x5 with k = 4, g = 0; move first.
python3 AI_runner.py 5 5 4 0 l ../src/connect-k-python/main.py SampleAIs/AverageAI_v2.pyc
echo "player 1 should win"


# 7x7 with k = 5, g = 0; move first.
python3 AI_runner.py 7 7 5 0 l ../src/connect-k-python/main.py SampleAIs/AverageAI_v2.pyc
echo "player 1 should win"