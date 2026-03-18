scores = []

while True:
    try:
        s = int(input())
        if s == -1:
            break
        elif 0 <= s <= 100:
            scores.append(s)
        else:
            print('錯誤')
    except ValueError:
        print('錯誤')

if len(scores) == 0:
    print('錯誤')
else:
    count = len(scores)
    avg = round(sum(scores) / count, 2)
    max_score = max(scores)
    min_score = min(scores)

A = len([x for x in scores if 90 <= x <= 100])
B = len([x for x in scores if 80 <= x <= 89])
C = len([x for x in scores if 70 <= x <= 79])
D = len([x for x in scores if 60 <= x <= 69])
E = len([x for x in scores if 0 <= x <= 59])

print(f'Count: {count}')
print(f'AVG: {avg}')
print(f'Max: {max_score}')
print(f'Min: {min_score}')

print(f'A: {A}, B:{B}, C:{C}, D:{D}, E:{E}')
