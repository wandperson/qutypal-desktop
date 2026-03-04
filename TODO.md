## Виправити масштабування вікна на Windows
Це змусить Qt правильно працювати з масштабуванням.
Треба перевірити.
```
app = QApplication(sys.argv)
app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
```

Увімкнути High DPI scaling
```
QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)
```

## Розрахунок робочої області
Замість того, щоб через WinAPI рахувати робочу область, у Qt є вже готовий метод, який враховує і панель задач, і DPI.
Треба перевірити.
```
screen = app.primaryScreen()
rect = screen.availableGeometry()  # робоча область (без панелі задач)
print(rect.x(), rect.y(), rect.width(), rect.height())
```

## Додаткові монітори
Якщо є кілька моніторів, можна отримати геометрію саме того монітора, де буде вікно.
Треба перевірити, можливо буде корисно у майбутньому.
```
screen = my_window.screen()
rect = screen.availableGeometry()
my_window.setGeometry(rect)
```