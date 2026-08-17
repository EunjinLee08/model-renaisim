# 사용 이미지
image c_lang01 = "clang_face0.png"
image c_lang01_mad = "clang_face1.png"
image python01 = "python_face0.png"
image python01_cry = "python_face1.png"
image vscode01 = "bg01.png"

# 상반신의 아래쪽이 대화창에 살짝 가려지도록 배치
transform c_lang_above_dialogue:
    xalign 0.15
    yanchor 1.0
    ypos 850

transform python_above_dialogue:
    xalign 0.75
    yanchor 1.0
    ypos 850

# 캐릭터 정의
define c_lang = Character('C', color='#00599C', image='c_lang01')
define char_python = Character('Python', color='#ecc434', image='python01')
define user = Character('개발자', color='#000000')
define system_log = Character('system', color='#c84747')

label start:
    scene vscode01
    show c_lang01 at c_lang_above_dialogue
    c_lang "인터프리터? 그런 걸 쓰는 걸 프로그래밍 언어라고 할 수 있어?"

    menu:
        "1. 당연히 컴파일러가 근본이지":
            c_lang "근본 정도가 아니라 기본이라고"
            jump python_run
        
        "2. 왜 그래. 인터프리터도 엄연히 언어야.":
            hide c_lang01
            show c_lang01_mad at c_lang_above_dialogue
            c_lang "HTML도 프로그래밍 언어라고 우기지 그래?"

    return

label python_run:
    show python01 at python_above_dialogue
    char_python "개, 개발자님... 방금 그 말 진심이세요...?"
    user "엇, 어엇....."
    hide python01
    show python01_cry at python_above_dialogue
    char_python "너무해요..!!"
    hide python01_cry
    system_log "-파이썬이 어디론가 달려가버렸다.-"
    user "어쩌지..."
    c_lang "포인터도 못 받아들이는 꼬맹이는 필요없어."
    user ";;"


label acid_rain:
    scene vscode01
    show c_lang01 at c_lang_above_dialogue
    c_lang "......."
    c_lang "아무튼"
    c_lang "하지만 말 뿐이라면 믿을 수 없어."
    c_lang "증명해 봐."

    call acid_rain_game
    $typing_result = _return
    $most_typed_category = typing_result["most_typed_category"]

    if typing_result["score"] <= 1000:
        c_lang "넌... 타자 연습부터 해야겠다."
    else:
        if most_type_category == "C":
            c_lang "역시"
        elif most_type_category == "Python":
            c_lang "허, 네 손은 자연스레 Python을 찾고 있는데?"

    return