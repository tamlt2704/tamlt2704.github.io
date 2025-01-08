with open("C:\\Users\\user\\WebstormProjects\\tamlt2704.github.io\\public\\hanzi\\dictionary.json", 'w', encoding='utf-8') as g:
    with open("C:\\Users\\user\\WebstormProjects\\tamlt2704.github.io\\public\\hanzi\\dictionary.txt", 'r', encoding='utf-8') as f:
        for line in f:
            g.write(f'{line.strip()},\n')