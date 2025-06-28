#import "TitlePage.typ": title-page

#let itmoPracticeReport(
  fontface: "New Computer Modern",
  body,
  ..titlepage-params,
) = {

  set page(
    paper: "a4",
    // размер полей (ГОСТ 7.0.11-2011, 5.3.7)
    margin: (top:2cm, bottom:2cm, left:2cm, right:2cm),
    // Установка сквозной нумерации страниц
    numbering: "1",
  )

  // Форматирование текста
  set text(
    font: "Times New Roman",
    fallback: false, // Включить резеврвные шрифты
    size: 12pt,
    lang: "ru",
    hyphenate: true, // Перенос по словам
  )

  set par(
    // Полуторный интервал (ГОСТ 7.0.11-2011, 5.3.6)
    leading: 1em,
    justify: true,
    linebreaks: "optimized",
    // Абзацный отступ. Должен быть одинаковым по всему тексту и равен пяти знакам (ГОСТ Р 7.0.11-2011, 5.3.7).
    first-line-indent: (
      all: true,
      amount: 2.5em,
    ),
  )

  title-page(..titlepage-params)

  set heading(numbering: "1.")
  body
}

#let introduction(body) = [
  #set heading(numbering: none)
  #heading[Введение]
  #body
]

#let conclusion(body) = [
  #set heading(numbering: none)
  #heading[Заключение]
  #body
]

#let annex(body) = [
  #set heading(numbering: none)
  #heading[Приложение]
  #body
]


