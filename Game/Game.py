import random, sys, pygame, ctypes

# Задаем значения констант:
HEARTS = chr(9829)
DIAMONDS = chr(9830)
SPADES = chr(9824)
CLUBS = chr(9827)
BACKSIDE = 'backside'

# Размер экрана
pygame.init()
screen = pygame.display.set_mode((1200, 600))

hwnd = pygame.display.get_wm_info()["window"]
ctypes.windll.user32.MoveWindow(hwnd, 320, 0, 1200, 600, True)

font = pygame.font.SysFont('Arial', 32)
fontMessage = pygame.font.SysFont('Arial', 16)
fontPlayers = pygame.font.SysFont('Arial', 24)
clock = pygame.time.Clock()
sprites = []
money = 5000
dealerHand = []
playerHand = []
showDealerHand = False
bet = 0
messages = []
buttonHit = pygame.Rect(360, 415, 100, 100)
buttonStand = pygame.Rect(455, 415, 100, 100)
buttonDouble = pygame.Rect(550, 415, 100, 100)
buttonEnter = pygame.Rect(360, 515, 100, 100)
buttonYes = pygame.Rect(220, 220, 150, 150)
buttonNo = pygame.Rect(420, 220, 150, 150)

def main():
    loadAssets()
    global money
    global dealerHand
    global playerHand
    global showDealerHand
    global bet
    global messages
    print('''Blackjack, by Al Sweigart al@inventwithpython.com

Правила:
  Постарайтесь набрать как можно больше очков, не превышая 21.
  Короли, дамы и валеты стоят 10 очков.
  Тузы может быть 1 или 11 очков.
  Карты со 2 по 10 стоят по их номиналу.
  (Х)ит - чтобы взять еще карту.
  (С)тенд - чтобы перестать брать карты.
  В первой игре вы можете сделать (Д)абл-даун, чтобы увеличить свою ставку,
  но вы получите ровно одну карту.
  В случае ничьей ставка возвращается игроку.
  Дилер прекращает брать карты после 17 очков.''')

    money = 5000
    while True:
        # Проверяем, не закончились ли у игрока деньги:
        if money <= 0:
            print("Вы на мели!")
            print("Хорошо, что вы играли не на реальные деньги.")
            print('Спасибо за игру!')
            sys.exit()

        # Даем возможность игроку сделать ставку на раунд:
        print('Деньги:', money)
        bet = getBet(money)

        # Сдаем дилеру и игроку по две карты из колоды:
        deck = getDeck()
        dealerHand = [deck.pop(), deck.pop()]
        playerHand = [deck.pop(), deck.pop()]

        # Проверяем возможность страховки/равных денег
        insuranceBet = 0
        evenMoneyTaken = False

        if dealerHand[0][0] == 'A':  # Если у дилера туз
            showDealerHand = False
            displayHands(playerHand, dealerHand, False)

            playerHasBlackjack = getHandValue(playerHand) == 21
            if playerHasBlackjack:
                print('Дилер раскрывает туз, и у вас в руках блэкджек!')
                print('"Равные деньги" — это страховка 1:1 вместо стандартных 3:2.')
                messagesClear()
                messages.append('Дилер раскрывает туз, и у вас в руках блэкджек!')
                messages.append('Равные деньги" — это страховка 1:1 вместо стандартных 3:2')
                messages.append('Хотите получить "равные деньги"?')
                screenUpdate()
                #choice = input('Хотите получить "равные деньги"? (ДА/НЕТ)').upper()

                choice = "q"
                while (choice != "Да" and choice != "Нет"):
                    screenUpdate('Равные деньги')
                    for event in pygame.event.get():
                        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonYes.collidepoint(
                                pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_y):
                            choice = 'Да'
                        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonNo.collidepoint(
                                pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_n):
                            choice = 'Нет'

                screenUpdate()
                if choice == 'ДА':
                    evenMoneyTaken = True
                    print('Вы взяли "равные деньги". Выигрыш:', bet)
                    messagesClear()
                    messages.append('Вы взяли "равные деньги". Выигрыш: ' + bet.__str__())
                    screenUpdate()
                    money += bet  # Выплата 1:1 сразу
            else:
                print('У дилера туз. Доступна страховка (половина от первоначальной ставки).')
                messagesClear()
                messages.append('У дилера туз')
                messages.append('Доступна страховка (половина от первоначальной ставки)')
                messages.append('Хотите получить страховку?')
                screenUpdate()
                choice = input('Хотите получить страховку? (ДА/НЕТ)').upper()
                if choice == 'ДА':
                    insuranceBet = bet // 2
                    print(f'Страховка: {insuranceBet}')
                    messagesClear()
                    messages.append('Да ' + f'Страховка: {insuranceBet}')
                    screenUpdate()
                    money -= insuranceBet
                else:
                    messages.append('Нет')

        # Проверяем блэкджек у дилера
        dealerHasBlackjack = getHandValue(dealerHand) == 21

        if dealerHasBlackjack:
            showDealerHand = True
            displayHands(playerHand, dealerHand, True)

            playerHasBlackjack = getHandValue(playerHand) == 21

            if playerHasBlackjack:
                if not evenMoneyTaken:
                    print('И у вас, и у дилера блэкджек! Ничья!')
                    messagesClear()
                    messages.append('И у вас, и у дилера блэкджек! Ничья!')
                    screenUpdate()
                    money += bet  # Возвращаем ставку
            else:
                print('У дилера блэкджек! Вы проиграли ставку.')
                messagesClear()
                messages.append('У дилера блэкджек! Вы проиграли ставку.')
                screenUpdate()
                money -= bet

                if insuranceBet > 0:
                    print('Но вы выиграли страховку! Выплата 2:1.')
                    messagesClear()
                    messages.append('У дилера блэкджек! Вы проиграли ставку')
                    messages.append('Но вы выиграли страховку! Выплата 2:1')
                    messages.append('Нажмите Enter, чтобы продолжить...')
                    screenUpdate()

                    move = ''
                    while (move != 'Enter'):
                        screenUpdate('Enter')
                        for event in pygame.event.get():
                            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonEnter.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                                move = 'Enter'
                    screenUpdate('Enter')


                    money += insuranceBet * 3  # +3 потому что 2:1 от страховки + возврат самой страховки

            screenUpdate()
            messagesClear()
            messages.append('Нажмите Enter, чтобы продолжить...')
            #input()

            move = ''
            while (move != 'Enter'):
                screenUpdate('Enter')
                for event in pygame.event.get():
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonEnter.collidepoint(
                            pygame.mouse.get_pos())) or (
                            event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                        move = 'Enter'
            screenUpdate()

            screenUpdate()
            print('\n\n')
            continue


        elif insuranceBet > 0:
            print('У дилера нет блэкджека. Вы потеряли страховку.')
            # Страховка уже вычтена ранее
            messagesClear()
            messages.append('У дилера нет блэкджека. Вы потеряли страховку')
            messages.append('Нажмите Enter, чтобы продолжить...')
            screenUpdate()
            move = ''
            move = ''
            while (move != 'Enter'):
                screenUpdate('Enter')
                for event in pygame.event.get():
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonEnter.collidepoint(
                            pygame.mouse.get_pos())) or (
                            event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                        move = 'Enter'
            screenUpdate()
            #input('Нажмите Enter, чтобы продолжить...')
            screenUpdate()
            print('\n\n')

        # Если игрок взял even money - пропускаем основной раунд
        if evenMoneyTaken:
            messagesClear()
            messages.append('Нажмите Enter, чтобы продолжить...')
            screenUpdate()
            move = ''
            while (move != 'Enter'):
                screenUpdate()
                for event in pygame.event.get():
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonEnter.collidepoint(
                            pygame.mouse.get_pos())) or (
                            event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                        move = 'Enter'
            screenUpdate('Enter')
            #input('Нажмите Enter, чтобы продолжить...')
            screenUpdate()
            print('\n\n')
            continue

        # Обработка действий игрока:
        print('Ставка:', bet)
        while True:  # Выполняем цикл до тех пор, пока игрок не скажет "хватит" или у него не будет перебор.
            showDealerHand = False
            displayHands(playerHand, dealerHand, False)
            print()

            # Проверка на перебор у игрока:
            if getHandValue(playerHand) > 21:
                break

            # Получаем ход игрока: Х, С или Д:
            move = getMove(playerHand, money - bet)

            # Обработка действий игрока:
            if move == 'Д':
                # Игрок удваивает, он может увеличить ставку:
                additionalBet = getBet(min(bet, (money - bet)))
                bet += additionalBet
                print('Ставка увеличена до {}.'.format(bet))
                messagesClear()
                messages.append('Ставка увеличена до {}.'.format(bet))
                screenUpdate()
                print('Ставка:', bet)

            if move in ('Х', 'Д'):
                # "хит" или "дабл-даун": игрок берет еще одну карту.
                newCard = deck.pop()
                rank, suit = newCard
                print('Вы получили {} из {}.'.format(rank, suit))
                messagesClear()
                messages.append('Вы получили {} из {}.'.format(rank, suit))
                screenUpdate()
                playerHand.append(newCard)

                if getHandValue(playerHand) > 21:
                    # Перебор у игрока:
                    continue

            if move in ('С', 'Д'):
                # "стенд" или "дабл-даун": переход хода к следующему игроку
                break

        # Обработка действий дилера:
        if getHandValue(playerHand) <= 21:
            while getHandValue(dealerHand) < 17:
                # Дилер берет еще карту:
                print('Дилер берет карту...')
                messagesClear()
                messages.append('Дилер берет карту...')
                screenUpdate()
                dealerHand.append(deck.pop())
                showDealerHand = False
                displayHands(playerHand, dealerHand, False)

                if getHandValue(dealerHand) > 21:
                    break  # Перебор у дилера.
            messagesClear()
            messages.append('Нажмите Enter, чтобы продолжить...')
            screenUpdate()
            #input('Нажмите Enter, чтобы продолжить...')
            move = ''
            while (move != 'Enter'):
                screenUpdate('Enter')
                for event in pygame.event.get():
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonEnter.collidepoint(
                            pygame.mouse.get_pos())) or (
                            event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                        move = 'Enter'
            screenUpdate()
            print('\n\n')

        # Отображаем итоговые карты на руках:
        showDealerHand = True
        displayHands(playerHand, dealerHand, True)

        playerValue = getHandValue(playerHand)
        dealerValue = getHandValue(dealerHand)
        # Проверяем, игрок выиграл, проиграл или сыграл вничью:
        message = ''
        if dealerValue > 21:
            message = 'Дилер проиграл! Вы выиграли ${}!'.format(bet)
            print('Дилер проиграл! Вы выиграли ${}!'.format(bet))
            money += bet
        elif (playerValue > 21) or (playerValue < dealerValue):
            message = 'Вы проиграли!'
            print('Вы проиграли!')
            money -= bet
        elif playerValue > dealerValue:
            message = 'Вы выиграли ${}!'.format(bet)
            print('Вы выиграли ${}!'.format(bet))
            money += bet
        elif playerValue == dealerValue:
            message = 'Ничья, ставка возвращена.'
            print('Ничья, ставка возвращена.')

        bet = 0

        messagesClear()
        messages.append(message)
        messages.append('Нажмите Enter, чтобы продолжить...')
        screenUpdate()
       # input('Нажмите Enter, чтобы продолжить...')
        move = ''
        while (move != 'Enter'):
            screenUpdate('Enter')
            for event in pygame.event.get():
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonEnter.collidepoint(
                        pygame.mouse.get_pos())) or (
                        event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                    move = 'Enter'
        screenUpdate()
        messages.clear()
        screenUpdate()
        print('\n\n')

        screenUpdate()
    pygame.quit()

def loadAssets():
    global sprites
    # Загружаем спрайты
    sprites.append(pygame.image.load("..\\Assets\\Backround.png"))
    sprites.append("Backround")
    sprites.append(pygame.image.load("..\\Assets\\Message_backround.png"))
    sprites.append("Message_backround")
    sprites.append(pygame.image.load("..\\Assets\\Button.png"))
    sprites.append("Button")
    sprites.append(pygame.image.load("..\\Assets\\Field.png"))
    sprites.append("Field")
    sprites.append(pygame.image.load("..\\Assets\\Money.png"))
    sprites.append("Money")
    sprites.append(pygame.image.load("..\\Cards\\Back Blue 1.png"))
    sprites.append("Back Blue 1")
    sprites.append(pygame.image.load("..\\Cards\\Back Blue 2.png"))
    sprites.append("Back Blue 2")
    sprites.append(pygame.image.load("..\\Cards\\Back Grey 1.png"))
    sprites.append("Back Grey 1")
    sprites.append(pygame.image.load("..\\Cards\\Back Grey 2.png"))
    sprites.append("Back Grey 2")
    sprites.append(pygame.image.load("..\\Cards\\Back Red 1.png"))
    sprites.append("Back Red 1")
    sprites.append(pygame.image.load("..\\Cards\\Back Red 2.png"))
    sprites.append("Back Red 2")
    sprites.append(pygame.image.load("..\\Cards\\Clubs 2.png"))
    sprites.append("Clubs_2")
    sprites.append(pygame.image.load("..\\Cards\\Clubs 3.png"))
    sprites.append("Clubs_3")
    sprites.append(pygame.image.load("..\\Cards\\Clubs 4.png"))
    sprites.append("Clubs_4")
    sprites.append(pygame.image.load("..\\Cards\\Clubs 5.png"))
    sprites.append("Clubs_5")
    sprites.append(pygame.image.load("..\\Cards\\Clubs 6.png"))
    sprites.append("Clubs_6")
    sprites.append(pygame.image.load("..\\Cards\\Clubs 7.png"))
    sprites.append("Clubs_7")
    sprites.append(pygame.image.load("..\\Cards\\Clubs 8.png"))
    sprites.append("Clubs_8")
    sprites.append(pygame.image.load("..\\Cards\\Clubs 9.png"))
    sprites.append("Clubs_9")
    sprites.append(pygame.image.load("..\\Cards\\Clubs 10.png"))
    sprites.append("Clubs_10")
    sprites.append(pygame.image.load("..\\Cards\\Clubs 1.png"))
    sprites.append("Clubs_A")
    sprites.append(pygame.image.load("..\\Cards\\Clubs 11.png"))
    sprites.append("Clubs_J")
    sprites.append(pygame.image.load("..\\Cards\\Clubs 13.png"))
    sprites.append("Clubs_K")
    sprites.append(pygame.image.load("..\\Cards\\Clubs 12.png"))
    sprites.append("Clubs_Q")
    sprites.append(pygame.image.load("..\\Cards\\Diamond 2.png"))
    sprites.append("Diamond_2")
    sprites.append(pygame.image.load("..\\Cards\\Diamond 3.png"))
    sprites.append("Diamond_3")
    sprites.append(pygame.image.load("..\\Cards\\Diamond 4.png"))
    sprites.append("Diamond_4")
    sprites.append(pygame.image.load("..\\Cards\\Diamond 5.png"))
    sprites.append("Diamond_5")
    sprites.append(pygame.image.load("..\\Cards\\Diamond 6.png"))
    sprites.append("Diamond_6")
    sprites.append(pygame.image.load("..\\Cards\\Diamond 7.png"))
    sprites.append("Diamond_7")
    sprites.append(pygame.image.load("..\\Cards\\Diamond 8.png"))
    sprites.append("Diamond_8")
    sprites.append(pygame.image.load("..\\Cards\\Diamond 9.png"))
    sprites.append("Diamond_9")
    sprites.append(pygame.image.load("..\\Cards\\Diamond 10.png"))
    sprites.append("Diamond_10")
    sprites.append(pygame.image.load("..\\Cards\\Diamond 1.png"))
    sprites.append("Diamond_A")
    sprites.append(pygame.image.load("..\\Cards\\Diamond 11.png"))
    sprites.append("Diamond_J")
    sprites.append(pygame.image.load("..\\Cards\\Diamond 13.png"))
    sprites.append("Diamond_K")
    sprites.append(pygame.image.load("..\\Cards\\Diamond 12.png"))
    sprites.append("Diamond_Q")
    sprites.append(pygame.image.load("..\\Cards\\Hearts 2.png"))
    sprites.append("Hearts_2")
    sprites.append(pygame.image.load("..\\Cards\\Hearts 3.png"))
    sprites.append("Hearts_3")
    sprites.append(pygame.image.load("..\\Cards\\Hearts 4.png"))
    sprites.append("Hearts_4")
    sprites.append(pygame.image.load("..\\Cards\\Hearts 5.png"))
    sprites.append("Hearts_5")
    sprites.append(pygame.image.load("..\\Cards\\Hearts 6.png"))
    sprites.append("Hearts_6")
    sprites.append(pygame.image.load("..\\Cards\\Hearts 7.png"))
    sprites.append("Hearts_7")
    sprites.append(pygame.image.load("..\\Cards\\Hearts 8.png"))
    sprites.append("Hearts_8")
    sprites.append(pygame.image.load("..\\Cards\\Hearts 9.png"))
    sprites.append("Hearts_9")
    sprites.append(pygame.image.load("..\\Cards\\Hearts 10.png"))
    sprites.append("Hearts_10")
    sprites.append(pygame.image.load("..\\Cards\\Hearts 1.png"))
    sprites.append("Hearts_A")
    sprites.append(pygame.image.load("..\\Cards\\Hearts 11.png"))
    sprites.append("Hearts_J")
    sprites.append(pygame.image.load("..\\Cards\\Hearts 13.png"))
    sprites.append("Hearts_K")
    sprites.append(pygame.image.load("..\\Cards\\Hearts 12.png"))
    sprites.append("Hearts_Q")
    sprites.append(pygame.image.load("..\\Cards\\Spades 2.png"))
    sprites.append("Spades_2")
    sprites.append(pygame.image.load("..\\Cards\\Spades 3.png"))
    sprites.append("Spades_3")
    sprites.append(pygame.image.load("..\\Cards\\Spades 4.png"))
    sprites.append("Spades_4")
    sprites.append(pygame.image.load("..\\Cards\\Spades 5.png"))
    sprites.append("Spades_5")
    sprites.append(pygame.image.load("..\\Cards\\Spades 6.png"))
    sprites.append("Spades_6")
    sprites.append(pygame.image.load("..\\Cards\\Spades 7.png"))
    sprites.append("Spades_7")
    sprites.append(pygame.image.load("..\\Cards\\Spades 8.png"))
    sprites.append("Spades_8")
    sprites.append(pygame.image.load("..\\Cards\\Spades 9.png"))
    sprites.append("Spades_9")
    sprites.append(pygame.image.load("..\\Cards\\Spades 10.png"))
    sprites.append("Spades_10")
    sprites.append(pygame.image.load("..\\Cards\\Spades 1.png"))
    sprites.append("Spades_A")
    sprites.append(pygame.image.load("..\\Cards\\Spades 11.png"))
    sprites.append("Spades_J")
    sprites.append(pygame.image.load("..\\Cards\\Spades 13.png"))
    sprites.append("Spades_K")
    sprites.append(pygame.image.load("..\\Cards\\Spades 12.png"))
    sprites.append("Spades_Q")

def screenUpdate(moves = [], value = 0):
    global screen
    global dealerHand
    global showDealerHand
    global messages

    global buttonHit
    global buttonStand
    global buttonDouble
    global buttonEnter
    global buttonYes
    global buttonNo

    screen.blit(sprites[sprites.index("Backround") - 1], (0, 0))
    screen.blit(sprites[sprites.index("Message_backround") - 1], (800, 0))
    screen.blit(pygame.transform.scale(sprites[sprites.index("Field") - 1], (150, 140)), (142, 398))
    screen.blit(pygame.transform.scale(sprites[sprites.index("Money") - 1], (50, 50)), (280, 440))
    screen.blit(font.render('Деньги:  ' + money.__str__(), True, (255, 255, 255)), (60, 450))
    screen.blit(pygame.transform.scale(sprites[sprites.index("Field") - 1], (150, 140)), (142, 448))
    screen.blit(pygame.transform.scale(sprites[sprites.index("Money") - 1], (50, 50)), (280, 490))
    screen.blit(font.render('Ставка:  ' + bet.__str__(), True, (255, 255, 255)), (60, 500))

    xPosition = 830
    yPosition = 50

    i = 0
    while (i < 10 and i < len(messages)):
        screen.blit(fontMessage.render(messages[i], True, (255, 255, 255)), (xPosition, yPosition))
        yPosition += 50
        i += 1

    xPosition = 60
    yPosition = 90

    if (showDealerHand == True):
        screen.blit(fontPlayers.render('Дилер: ' + getHandValue(dealerHand).__str__(), True, (255, 255, 255)), (60, 50))
        for i in range(0, len(dealerHand)):
            card = dealerHand[i:(i+1)]
            rank, suit = card[0]
            if (suit == chr(9829)):
                suit = 'Hearts'
            if (suit == chr(9830)):
                suit = 'Diamond'
            if (suit == chr(9824)):
                suit = 'Spades'
            if (suit == chr(9827)):
                suit = 'Clubs'
            name = suit + '_' + rank
            screen.blit(sprites[sprites.index(name) - 1], (xPosition, yPosition))
            xPosition += 120
    else:
        number = 0
        hide = 0
        screen.blit(fontPlayers.render('Дилер: ???', True, (255, 255, 255)), (60, 50))
        for i in range(0, len(dealerHand)):
            card = dealerHand[i:(i + 1)]
            rank, suit = card[0]
            if (suit == chr(9829)):
                suit = 'Hearts'
            if (suit == chr(9830)):
                suit = 'Diamond'
            if (suit == chr(9824)):
                suit = 'Spades'
            if (suit == chr(9827)):
                suit = 'Clubs'
            name = suit + '_' + rank
            if (rank == 'A' and i == 0):
                hide = 1
            if (number != hide):
                screen.blit(sprites[sprites.index(name) - 1], (xPosition, yPosition))
            else:
                if (suit == 'Hearts' or suit == 'Diamond'):
                    screen.blit(sprites[sprites.index('Back Red 2') - 1], (xPosition, yPosition))
                else:
                    screen.blit(sprites[sprites.index("Back Grey 2") - 1], (xPosition, yPosition))
            xPosition += 120
            number += 1

    xPosition = 60
    yPosition = 270

    screen.blit(fontPlayers.render('Игрок: ' + getHandValue(playerHand).__str__(), True, (255, 255, 255)), (60, 230))
    for i in range(0, len(playerHand)):
        card = playerHand[i:(i+1)]
        rank, suit = card[0]
        if (suit == chr(9829)):
            suit = 'Hearts'
        if (suit == chr(9830)):
            suit = 'Diamond'
        if (suit == chr(9824)):
            suit = 'Spades'
        if (suit == chr(9827)):
            suit = 'Clubs'
        name = suit + '_' + rank
        screen.blit(sprites[sprites.index(name) - 1], (xPosition, yPosition))
        xPosition += 120


    screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (100, 100)), (360, 415))
    screen.blit(fontMessage.render('(Х)ит', True, (255, 255, 255)), (395, 454))
    screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (100, 100)), (455, 415))
    screen.blit(fontMessage.render('(С)тенд', True, (255, 255, 255)), (480, 454))
    screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (100, 100)), (550, 415))
    screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (100, 100)), (360, 470))

    if ('(Д)абл-даун' in moves):
        screen.blit(fontMessage.render('(Д)абл-даун', True, (255, 255, 255)), (563, 454))

    if ('(Д)абл-даун' not in moves):
        screen.blit(fontMessage.render('', True, (255, 255, 255)), (563, 454))

    if ('Enter' in moves):
        screen.blit(fontMessage.render('Enter', True, (255, 255, 255)), (395, 510))

    if ('Enter' not in moves):
        screen.blit(fontMessage.render('', True, (255, 255, 255)), (395, 510))

    if buttonHit.collidepoint(pygame.mouse.get_pos()):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (110, 110)), (355, 410))
        screen.blit(fontMessage.render('(Х)ит', True, (255, 255, 255)), (395, 454))

    if buttonStand.collidepoint(pygame.mouse.get_pos()):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (110, 110)), (450, 410))
        screen.blit(fontMessage.render('(С)тенд', True, (255, 255, 255)), (480, 454))

    if buttonDouble.collidepoint(pygame.mouse.get_pos()) and '(Д)абл-даун' in moves:
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (110, 110)), (545, 410))
        screen.blit(fontMessage.render('(Д)абл-даун', True, (255, 255, 255)), (563, 454))

    if buttonEnter.collidepoint(pygame.mouse.get_pos()) and 'Enter' in moves:
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (110, 110)), (355, 465))
        screen.blit(fontMessage.render('Enter', True, (255, 255, 255)), (395, 510))

    if ('Ставка' in moves):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (150, 120))
        screen.blit(font.render("Введите ставку", True, (255, 255, 255)), (300, 200))
        screen.blit(font.render(value.__str__(), True,  (255, 255, 255)), (300, 270))

    if ('Равные деньги' in moves):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (150, 120))
        screen.blit(font.render('Хотите получить "равные деньги"?', True, (255, 255, 255)), (185, 200))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (220, 220))
        if buttonYes.collidepoint(pygame.mouse.get_pos()):
            screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (180, 180)), (205, 205))
        screen.blit(fontPlayers.render('Да', True, (255, 255, 255)), (280, 280))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (420, 220))
        if buttonNo.collidepoint(pygame.mouse.get_pos()):
            screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (180, 180)), (405, 205))
        screen.blit(fontPlayers.render('Нет', True, (255, 255, 255)), (480, 280))



    pygame.display.flip()

def messagesClear():
    global messages
    if (len(messages) > 10):
        messages.clear()

def getBet(maxBet):
    value = ""
    """Спрашиваем у игрока, сколько он ставит на этот раунд."""
    while True:  # Продолжаем спрашивать, пока не будет введено допустимое значение.
        # print('Сколько вы ставите? (1-{}, or ВЫХОД)'.format(maxBet))
        # screenUpdate()
        # bet = input('> ').upper().strip()
        # screenUpdate()
        # if bet == 'ВЫХОД':
        #     print('Спасибо за игру!')
        #     sys.exit()
        screenUpdate('Ставка', value)
        for event in pygame.event.get():
            if (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_RETURN and value != "" and value != "0"):
                    return int(value)
                elif (event.key == pygame.K_BACKSPACE):
                    value = value[:-1]
                else:
                    if (event.unicode.isdigit()):
                        value += event.unicode
                        if (int(value) > maxBet):
                            value = value[:-1]

       # if not bet.isdecimal():
         #   continue  # Если игрок не ответил — спрашиваем снова.

        #bet = int(bet)
        # bet = int(value)
        # if 1 <= bet <= maxBet:
        #     return bet  # Игрок ввел допустимое значение ставки.


def getDeck():
    """Возвращаем список кортежей (номинал, масть) для всех 52 карт."""
    deck = []
    for suit in (HEARTS, DIAMONDS, SPADES, CLUBS):
        for rank in range(2, 11):
            deck.append((str(rank), suit))  # Добавляем числовые карты.
        for rank in ('J', 'Q', 'K', 'A'):
            deck.append((rank, suit))  # Добавляем фигурные карты и тузы.
    random.shuffle(deck)
    return deck


def displayHands(playerHand, dealerHand, showDealerHand):
    """Отображаем карты игрока и дилера. Скрываем первую карту дилера,
    если showDealerHand равно False."""
    print()
    if showDealerHand:
        print('Дилер:', getHandValue(dealerHand))
        displayCards(dealerHand)
    else:
        print('Дилер: ???')
        # Если у дилера туз вверх - показываем его
        if dealerHand[0][0] == 'A':
            displayCards([dealerHand[0]] + [BACKSIDE] + dealerHand[2:])
        else:
            displayCards([BACKSIDE] + dealerHand[1:])

    # Отображаем карты игрока:
    print('Игрок:', getHandValue(playerHand))
    displayCards(playerHand)


def getHandValue(cards):
    """Возвращаем стоимость карт. Фигурные карты стоят 10, тузы — 11
    или 1 очко (эта функция выбирает подходящую стоимость карты)."""
    value = 0
    numberOfAces = 0

    # Добавляем стоимость карты — не туза:
    for card in cards:
        rank = card[0]  # карта представляет собой кортеж (номинал, масть)
        if rank == 'A':
            numberOfAces += 1
        elif rank in ('K', 'Q', 'J'):  # Фигурные карты стоят 10 очков.
            value += 10
        else:
            value += int(rank)  # Стоимость числовых карт равна их номиналу.

    # Добавляем стоимость для тузов:
    value += numberOfAces  # Добавляем 1 для каждого туза.
    for i in range(numberOfAces):
        # Если можно добавить еще 10 с перебором, добавляем:
        if value + 10 <= 21:
            value += 10

    return value


def displayCards(cards):
    """Отображаем все карты из списка карт."""
    rows = ['', '', '', '', '']  # Отображаемый в каждой строке текст.

    for i, card in enumerate(cards):
        rows[0] += ' ___ '  # Выводим верхнюю строку карты.
        if card == BACKSIDE:
            # Выводим рубашку карты:
            rows[1] += '|## | '
            rows[2] += '|###| '
            rows[3] += '|_##| '
        else:
            # Выводим лицевую сторону карты:
            rank, suit = card  # Карта — структура данных типа кортеж.
            rows[1] += '|{} | '.format(rank.ljust(2))
            rows[2] += '| {} | '.format(suit)
            rows[3] += '|_{}| '.format(rank.rjust(2, '_'))

    # Выводим все строки на экран:
    for row in rows:
        print(row)


def getMove(playerHand, money):
    global buttonHit
    """Спрашиваем, какой ход хочет сделать игрок, и возвращаем 'Х', если он
    хочет взять еще карту, 'С', если ему хватит, и 'Д', если он удваивает."""
    while True:  # Продолжаем итерации цикла, пока игрок не сделает допустимый ход.
        # Определяем, какие ходы может сделать игрок:
        moves = ['(Х)ит', '(С)тенд']

        # Игрок может удвоить при первом ходе, это ясно из того,
        # что у игрока ровно две карты:
        if len(playerHand) == 2 and money > 0:
            moves.append('(Д)абл-даун')

        # Получаем ход игрока:
        movePrompt = ', '.join(moves) + '> '
        screenUpdate(moves)
        #move = input(movePrompt).upper()
        move = 'q'
        while (move == 'q'):
            screenUpdate(moves)
            for event in pygame.event.get():
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonHit.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_x):
                    move = 'Х'
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonStand.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_c):
                    move = 'С'
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonDouble.collidepoint(pygame.mouse.get_pos()) and '(Д)абл-даун' in moves) or (event.type == pygame.KEYDOWN and event.key == pygame.K_d  and '(Д)абл-даун' in moves):
                    move = 'Д'
        screenUpdate(moves)
        if move in ('Х', 'С'):
            return move  # Игрок сделал допустимый ход.
        if move == 'Д' and '(Д)абл-даун' in moves:
            return move  # Игрок сделал допустимый ход.


# Если программа не импортируется, а запускается, производим запуск:
if __name__ == '__main__':
   main()