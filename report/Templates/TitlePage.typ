// Титульный лист (ГОСТ Р 7.0.11-2001, 5.1)
#let title-page(
  organization: (
    full: "Национальный Исследовательский Университет ИТМО",
    short:"Университет ИТМО",
    logo: "logo_basic_russian_black.svg"
  ),
  city: "Город",
  year: datetime.today().year(),

  title: "Название работы",
  abstract: "Опишите здесь что вы сделали в работе с точки зрения исследования. Что вы для себя открыли? С какими трудностями столкнулись? Какие технологии использовали? Если есть, что интересное еще рассказать, обязательно добавляйте.",
  keywords: ("Ключевые", "слова"),

  author: (
    name: "Фамилия Имя Отчество",
    isu: "123456",
  ),
  supervisor: (
    name: "Фамилия Имя Отчество",
    regalia: "Должность",
  ),
) = {

  // Настройки
  set page(numbering: {})
  set par(
    leading: 0.7em, justify: false
  )
  set text(hyphenate: false)
  set align(center)

  v(3em)

  // Огранизация
  if organization.logo.len() > 0 {
    image(organization.logo, width: 50%)
  } else [
    LOGO
  ]
  [Факультет Систем Управления и Робототехники]

  v(7em)

  text(16pt)[*#title*]

  v(5em)


  // text(16pt)[#author-full-name]
  grid(columns: (2fr, 1fr),
    [
        #set par(justify: true)
        #set text(hyphenate: false)
        #set align(left)

        #h(2em)
        *Аннтоация* – #abstract

        *Ключевые слова:* #keywords.join("; ")
    ],
    []
  )

  v(3em)

  align(right)[

    *Практику проходил*: \
    студент 2-го курса, #author.isu \
    #author.name

    *Руководитель*: \
    #supervisor.regalia \
    #supervisor.name
  ]

  v(1fr)

  [#city #year]
}
