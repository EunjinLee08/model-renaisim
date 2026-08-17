# 산성비 타자 미니게임

# 게임 설정
# 코드 추가 시 category는 "C" 또는 "Python"으로 지정합니다.
define ACID_RAIN_TICK = 0.05
define ACID_RAIN_DURATION = 45.0
define ACID_RAIN_MAX_LIVES = 5
define ACID_RAIN_CODE_FONT = "MonaFont-ttf/Mona/01 Main/Mona10.ttf"

default acid_rain_input = ""
default acid_rain_active_words = []
default acid_rain_stats = {}
default acid_rain_score = 0
default acid_rain_lives = 5
default acid_rain_elapsed = 0.0
default acid_rain_spawn_elapsed = 0.0
default acid_rain_next_id = 0
default acid_rain_wrong_inputs = 0
default acid_rain_finished = False

init python:
    ACID_RAIN_WORDS = [
        {"text": "#include <stdio.h>", "category": "C"},
        {"text": "int main(void)", "category": "C"},
        {"text": "for (int i = 0; i < 10; i++)", "category": "C"},
        {"text": "if (x >= 10 && y != 0)", "category": "C"},
        {"text": "char *name = \"C\";", "category": "C"},
        {"text": "return 0;", "category": "C"},
        {"text": "def main():", "category": "Python"},
        {"text": "print(\"Hello, world!\")", "category": "Python"},
        {"text": "for i in range(10):", "category": "Python"},
        {"text": "if x >= 10 and y != 0:", "category": "Python"},
        {"text": "items.append(value)", "category": "Python"},
        {"text": "result = {\"score\": 100}", "category": "Python"},
        {"text": "values = [x * 2 for x in items]", "category": "Python"},
        {"text": "path = \"C:\\\\temp\\\\file.txt\"", "category": "Python"},
    ]
    ACID_RAIN_CATEGORIES = ("C", "Python")

    def acid_rain_escape_code(code):
        # 동적 코드가 Ren'Py의 {text tag}나 [substitution]으로 해석되지 않게 합니다.
        return code.replace("{", "{{").replace("[", "[[")

    def acid_rain_empty_stat():
        return {
            "appeared": 0,
            "correct": 0,
            "missed": 0,
            "response_times": [],
        }

    def acid_rain_reset():
        store = renpy.store
        store.acid_rain_input = ""
        store.acid_rain_active_words = []
        store.acid_rain_stats = {
            category: acid_rain_empty_stat()
            for category in ACID_RAIN_CATEGORIES
        }
        store.acid_rain_score = 0
        store.acid_rain_lives = ACID_RAIN_MAX_LIVES
        store.acid_rain_elapsed = 0.0
        store.acid_rain_spawn_elapsed = 0.0
        store.acid_rain_next_id = 0
        store.acid_rain_wrong_inputs = 0
        store.acid_rain_finished = False
        acid_rain_spawn_word()

    def acid_rain_spawn_word():
        store = renpy.store
        source = renpy.random.choice(ACID_RAIN_WORDS)
        word = {
            "id": store.acid_rain_next_id,
            "text": source["text"],
            "category": source["category"],
            # 긴 코드가 화면 좌우 밖으로 잘리지 않도록 중앙 영역에 생성합니다.
            "x": renpy.random.randint(380, 1540),
            "y": 135.0,
            "speed": renpy.random.uniform(30.0, 50.0),
            "born_at": store.acid_rain_elapsed,
        }
        store.acid_rain_next_id += 1
        store.acid_rain_active_words.append(word)
        store.acid_rain_stats[word["category"]]["appeared"] += 1

    def acid_rain_spawn_interval():
        # 시간이 지날수록 1.35초에서 0.75초까지 출제 간격이 짧아집니다.
        progress = min(1.0, renpy.store.acid_rain_elapsed / ACID_RAIN_DURATION)
        return 1.35 - (0.60 * progress)

    def acid_rain_finish():
        store = renpy.store
        if store.acid_rain_finished:
            return

        # 제한 시간이 끝났을 때 화면에 남은 단어도 놓친 단어로 집계합니다.
        for word in store.acid_rain_active_words:
            store.acid_rain_stats[word["category"]]["missed"] += 1
        store.acid_rain_active_words = []
        store.acid_rain_finished = True
        store.acid_rain_input = ""

    def acid_rain_tick(delta=ACID_RAIN_TICK):
        store = renpy.store
        if store.acid_rain_finished:
            return

        store.acid_rain_elapsed += delta
        store.acid_rain_spawn_elapsed += delta

        remaining_words = []
        for word in store.acid_rain_active_words:
            word["y"] += word["speed"] * delta
            if word["y"] >= 890:
                store.acid_rain_stats[word["category"]]["missed"] += 1
                store.acid_rain_lives -= 1
            else:
                remaining_words.append(word)
        store.acid_rain_active_words = remaining_words

        if store.acid_rain_lives <= 0 or store.acid_rain_elapsed >= ACID_RAIN_DURATION:
            acid_rain_finish()
            return

        interval = acid_rain_spawn_interval()
        if store.acid_rain_spawn_elapsed >= interval:
            store.acid_rain_spawn_elapsed -= interval
            acid_rain_spawn_word()

    def acid_rain_submit():
        store = renpy.store
        # 코드에서는 공백도 정답의 일부이므로 입력을 strip하지 않습니다.
        typed = store.acid_rain_input
        store.acid_rain_input = ""

        if not typed or store.acid_rain_finished:
            return

        matches = [
            word for word in store.acid_rain_active_words
            if word["text"] == typed
        ]
        if not matches:
            store.acid_rain_wrong_inputs += 1
            return

        # 같은 단어가 여러 개라면 바닥에 가장 가까운 단어를 제거합니다.
        target = max(matches, key=lambda word: word["y"])
        store.acid_rain_active_words = [
            word for word in store.acid_rain_active_words
            if word["id"] != target["id"]
        ]

        stat = store.acid_rain_stats[target["category"]]
        stat["correct"] += 1
        stat["response_times"].append(
            max(0.0, store.acid_rain_elapsed - target["born_at"])
        )
        store.acid_rain_score += 100
        # Function 액션은 None이 아닌 값을 call screen의 결과로 전달하므로,
        # Enter 입력만으로 화면이 종료되지 않도록 값을 반환하지 않습니다.
        return

    def acid_rain_category_accuracy(category):
        stat = renpy.store.acid_rain_stats[category]
        if stat["appeared"] == 0:
            return 0.0
        return stat["correct"] * 100.0 / stat["appeared"]

    def acid_rain_category_average_time(category):
        times = renpy.store.acid_rain_stats[category]["response_times"]
        if not times:
            return 0.0
        return sum(times) / len(times)

    def acid_rain_make_result():
        store = renpy.store
        categories = {}
        for category in ACID_RAIN_CATEGORIES:
            stat = store.acid_rain_stats[category]
            categories[category] = {
                "appeared": stat["appeared"],
                "correct": stat["correct"],
                "missed": stat["missed"],
                "accuracy": round(acid_rain_category_accuracy(category), 1),
                "average_time": round(acid_rain_category_average_time(category), 2),
            }

        c_correct = categories["C"]["correct"]
        python_correct = categories["Python"]["correct"]
        if c_correct > python_correct:
            most_typed_category = "C"
        elif python_correct > c_correct:
            most_typed_category = "Python"
        else:
            most_typed_category = "tie"

        return {
            "score": store.acid_rain_score,
            "correct": sum(item["correct"] for item in categories.values()),
            "missed": sum(item["missed"] for item in categories.values()),
            "wrong_inputs": store.acid_rain_wrong_inputs,
            "categories": categories,
            "most_typed_category": most_typed_category,
        }

screen acid_rain_screen():
    modal True
    zorder 100

    add Solid("#101827")

    frame:
        xfill True
        ysize 110
        background Solid("#17233acc")

        hbox:
            xalign 0.5
            yalign 0.5
            spacing 120

            text "점수 [acid_rain_score]" size 38 color "#ffffff"
            text "기회 [acid_rain_lives]/[ACID_RAIN_MAX_LIVES]" size 38 color "#ff8b8b"
            text "남은 시간 [max(0, int(ACID_RAIN_DURATION - acid_rain_elapsed))]초" size 38 color "#8ed8ff"

    if not acid_rain_finished:
        timer ACID_RAIN_TICK repeat True action Function(acid_rain_tick, ACID_RAIN_TICK)
        key "K_RETURN" action Function(acid_rain_submit)
        key "K_KP_ENTER" action Function(acid_rain_submit)

        for word in acid_rain_active_words:
            frame:
                xpos int(word["x"])
                ypos int(word["y"])
                xanchor 0.5
                yanchor 0.5
                padding (18, 10)
                background Solid("#28466ee6")

                text acid_rain_escape_code(word["text"]):
                    font ACID_RAIN_CODE_FONT
                    size 30
                    color "#ffffff"

        frame:
            xalign 0.5
            ypos 930
            xsize 1500
            ysize 105
            padding (25, 14)
            background Solid("#f5f7fb")

            input:
                value VariableInputValue("acid_rain_input")
                length 80
                xalign 0.5
                yalign 0.5
                font ACID_RAIN_CODE_FONT
                size 34
                color "#152238"
                caret Solid("#152238")

        text "코드를 정확히 입력하고 Enter를 누르세요":
            xalign 0.5
            ypos 900
            size 26
            color "#a9bad4"

    else:
        add Solid("#000000aa")

        frame:
            xalign 0.5
            yalign 0.5
            xsize 1180
            padding (55, 45)
            background Solid("#f5f7fb")

            vbox:
                xfill True
                spacing 24

                text "타자 결과":
                    xalign 0.5
                    size 52
                    color "#152238"

                text "총점 [acid_rain_score]점 · 오입력 [acid_rain_wrong_inputs]회":
                    xalign 0.5
                    size 32
                    color "#354760"

                null height 8

                hbox:
                    xfill True
                    spacing 45

                    text "단어군" xsize 180 size 30 bold True color "#152238"
                    text "출제" xsize 130 size 30 bold True color "#152238"
                    text "성공" xsize 130 size 30 bold True color "#152238"
                    text "놓침" xsize 130 size 30 bold True color "#152238"
                    text "정확도" xsize 170 size 30 bold True color "#152238"
                    text "평균 반응" size 30 bold True color "#152238"

                for category in ACID_RAIN_CATEGORIES:
                    $ stat = acid_rain_stats[category]
                    $ accuracy = acid_rain_category_accuracy(category)
                    $ average_time = acid_rain_category_average_time(category)

                    hbox:
                        xfill True
                        spacing 45

                        text category xsize 180 size 30 color "#354760"
                        text str(stat["appeared"]) xsize 130 size 30 color "#354760"
                        text str(stat["correct"]) xsize 130 size 30 color "#257447"
                        text str(stat["missed"]) xsize 130 size 30 color "#b33d45"
                        text ("%.1f%%" % accuracy) xsize 170 size 30 color "#354760"
                        text ("%.2f초" % average_time) size 30 color "#354760"

                null height 12

                textbutton "스토리로 돌아가기":
                    xalign 0.5
                    padding (34, 16)
                    text_size 32
                    action Return(acid_rain_make_result())

label acid_rain_game:
    $ acid_rain_reset()
    call screen acid_rain_screen
    return _return
