import random, sys, pygame, ctypes

# Задаем значения констант:
HEARTS = chr(9829)
DIAMONDS = chr(9830)
SPADES = chr(9824)
CLUBS = chr(9827)
BACKSIDE = 'backside'

ctypes.windll.shcore.SetProcessDpiAwareness(1)

pygame.init()
screen = pygame.display.set_mode((1920, 1080), pygame.NOFRAME)

font = pygame.font.SysFont('Arial', 32)
fontMessage = pygame.font.SysFont('Arial', 16)
fontPlayers = pygame.font.SysFont('Arial', 24)
clock = pygame.time.Clock()
sprites = []
money = 5000
dealerHand = []
playerHand = []
playerHands = []
showDealerHand = False
bet = 0
bets = []
messages = []
buttonHit = pygame.Rect(1450, 800, 100, 100)
buttonStand = pygame.Rect(1550, 800, 100, 100)
buttonDouble = pygame.Rect(1650, 800, 100, 100)
buttonSurrender = pygame.Rect(1450, 900, 100, 100)
buttonEnter = pygame.Rect(1750, 800, 100, 100)
buttonYes = pygame.Rect(690, 550, 150, 150)
buttonNo = pygame.Rect(880, 550, 150, 150)
buttonEnd = pygame.Rect(690, 550, 150, 150)
buttonExit = pygame.Rect(1750, -45, 150, 150)
buttonContinue = pygame.Rect(880, 550, 150, 150)
buttonRules = pygame.Rect(1550, 900, 100, 100)
victory = pygame.mixer.Sound("..\\Sounds\\victory_sound.mp3")
cardFlick = pygame.mixer.Sound("..\\Sounds\\card_flick.mp3")

def main():
    loadAssets()
    global money
    global dealerHand
    global playerHand
    global playerHands
    global showDealerHand
    global bet
    global bets
    global messages
    global victory

    pygame.mixer.music.set_volume(0.01)
    pygame.mixer.music.play()
    money = 5000
    while True:
        # Проверяем, не закончились ли у игрока деньги:
        if money <= 0:
            screenUpdate('End')
            move = ''
            while (move == ''):
                screenUpdate('End')
                for event in pygame.event.get():
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonEnd.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        move = 'Exit'
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonContinue.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_r):
                        move = 'Restart'
                if (move == 'Exit'):
                    sys.exit()
                if (move == 'Restart'):
                    money = 5000

        # Даем возможность игроку сделать ставку на раунд:
        bet = getBet(money)
        showDealerHand = False

        # Сдаем дилеру и игроку по две карты из колоды:
        deck = getDeck()
        dealerHand = [deck.pop(), deck.pop()]
        playerHands = [[deck.pop(), deck.pop()]]  # Теперь это список рук игрока

        currentHandIndex = 0
        bets = [bet]  # Список ставок для каждой руки
        insuranceBets = [0]  # Список страховок для каждой руки
        evenMoneyTaken = False
        surrendered = [False]  # Список флагов отступных для каждой руки

        # Проверяем возможность страховки/равных денег
        insuranceBet = 0
        evenMoneyTaken = False

        if dealerHand[0][0] == 'A':  # Если у дилера туз
            showDealerHand = False
            #displayHands(playerHand, dealerHand, False)

            playerHasBlackjack = getHandValue(playerHand) == 21
            if playerHasBlackjack:
                messagesClear()
                messages.append('Дилер раскрывает туз, и у вас в руках блэкджек!')
                messages.append('Равные деньги" — это страховка 1:1 вместо стандартных 3:2')
                screenUpdate()

                choice = ''
                while (choice == ''):
                    screenUpdate('Равные деньги')
                    for event in pygame.event.get():
                        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonYes.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_y):
                            choice = 'Да'
                        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonNo.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_n):
                            choice = 'Нет'

                screenUpdate()
                if choice == 'ДА':
                    evenMoneyTaken = True
                    messagesClear()
                    messages.append('Вы взяли "равные деньги". Выигрыш: ' + bet.__str__())
                    screenUpdate()
                    money += bet  # Выплата 1:1 сразу
            else:
                messagesClear()
                messages.append('У дилера туз')
                messages.append('Доступна страховка (половина от первоначальной ставки)')
                messages.append('Хотите получить страховку?')
                screenUpdate()
                choice = "q"
                while (choice != "Да" and choice != "Нет"):
                    screenUpdate('Страховка')
                    for event in pygame.event.get():
                        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonYes.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_y):
                            choice = 'Да'
                        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonNo.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_n):
                            choice = 'Нет'
                if choice == 'Да':
                    insuranceBet = bet // 2
                    messagesClear()
                    messages.append('Да ' + f'Страховка: {insuranceBet}')
                    screenUpdate()
                    money -= insuranceBet
                else:
                    messages.append('Нет')
                    screenUpdate()

        dealerHasBlackjack = getHandValue(dealerHand) == 21

        if dealerHasBlackjack:
            showDealerHand = True
            playerHasBlackjack = getHandValue(playerHand) == 21

            if playerHasBlackjack:
                if not evenMoneyTaken:
                    messagesClear()
                    messages.append('И у вас, и у дилера блэкджек! Ничья!')
                    screenUpdate()
                    money += bet  # Возвращаем ставку
            else:
                messagesClear()
                messages.append('У дилера блэкджек! Вы проиграли ставку.')
                screenUpdate()
                money -= bet

                if insuranceBet > 0:
                    messages.append('Но вы выиграли страховку! Выплата 2:1')
                    messages.append('Нажмите Enter, чтобы продолжить...')
                    screenUpdate()

                    move = ''
                    while (move != 'Enter'):
                        screenUpdate('Enter')
                        for event in pygame.event.get():
                            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonEnter.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                                move = 'Enter'
                    screenUpdate(move)

                    money += insuranceBet * 3  # +3 потому что 2:1 от страховки + возврат самой страховки

            screenUpdate()
            messagesClear()
            messages.append('Нажмите Enter, чтобы продолжить...')
            screenUpdate()

            move = ''
            while (move == ''):
                screenUpdate('Enter')
                for event in pygame.event.get():
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonEnter.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                        move = 'Enter'
            screenUpdate(move)
            continue

        elif insuranceBet > 0:
            # Страховка уже вычтена ранее
            messagesClear()
            messages.append('У дилера нет блэкджека. Вы потеряли страховку')
            messages.append('Нажмите Enter, чтобы продолжить...')
            screenUpdate()
            move = ''
            while (move == ''):
                screenUpdate('Enter')
                for event in pygame.event.get():
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonEnter.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                        move = 'Enter'
            screenUpdate(move)
            screenUpdate()

        # Если игрок взял even money - пропускаем основной раунд
        if evenMoneyTaken:
            messagesClear()
            messages.append('Нажмите Enter, чтобы продолжить...')
            screenUpdate()
            move = ''
            while (move != 'Enter'):
                screenUpdate()
                for event in pygame.event.get():
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonEnter.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                        move = 'Enter'
            screenUpdate('move')
            continue

        # Обработка всех рук игрока
        while currentHandIndex < len(playerHands):
            playerHand = playerHands[currentHandIndex]
            bet = bets[currentHandIndex]
            initialBet = bet # Сохраняем первоначальную ставку для текущей руки
            # Проверяем первоначальную ставку для текущей руки
            if len(playerHand) == 2 and canSplit(playerHand) and money >= bet:
                rank1,_=playerHand[0]
                rank2,_=playerHand[1]
                if rank1 == rank2:
                    move = ''
                    while (move != 'P' and move != 'N'):
                        screenUpdate('Разбиение')
                        for event in pygame.event.get():
                            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonYes.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_y):
                                move = 'P'
                            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonNo.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_n):
                                move = 'N'
                    screenUpdate(move)

                    if move == 'P':
                        #  Вычитаем дополнительную ставку
                        money -= bet
                        bets.append(bet)
                        insuranceBets.append(0)
                        surrendered.append(False)

                        # Разбиваем руку
                        newHand1 = [playerHand[0], deck.pop()]
                        newHand2 = [playerHand[1], deck.pop()]

                        # Заменяем текущую руку и добавляем новую
                        playerHands[currentHandIndex] = newHand1
                        playerHands.append(newHand2)

                        # Показываем новые руки
                        screenUpdate()

                        messagesClear()
                        messages.append("нажмите enter чтобы продолжить")
                        screenUpdate()
                        move = ''
                        while (move != 'Enter'):
                            screenUpdate('Enter')
                            for event in pygame.event.get():
                                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonEnter.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                                    move = 'Enter'
                        screenUpdate(move)

                        # Переходим к обработке первой руки после сплита
                        continue

                    # Обработка действий для текущей руки:
                    messages.append(f'\nОбрабатывается рука {currentHandIndex + 1} из {len(playerHands)}')
                    screenUpdate()

                    while True:  # Выполняем цикл до тех пор, пока игрок не скажет "хватит" или у него не будет перебор.
                        # Проверка на перебор у игрока:
                        if getHandValue(playerHand) > 21:
                            break

                        # Получаем ход игрока: Х, С, О или Д:
                        move = getMove(playerHand, money - sum(bets), len(playerHands) > 1)

                        # Обработка отступных
                        if move == 'О':
                            screenUpdate('Surrender')
                            surrendered[currentHandIndex] = True
                            surrenderAmount = bet // 2
                            messagesClear()
                            messages.append(f'Вы выбрали отступные. Возвращаем {surrenderAmount}')
                            screenUpdate()
                            money -= surrenderAmount
                            move = ''
                            while (move != 'Enter'):
                                screenUpdate('Enter')
                                for event in pygame.event.get():
                                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonEnter.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                                        move = 'Enter'
                            screenUpdate(move)
                            break  # Завершаем текущую руку

                        # Игрок удваивает, он может увеличить ставку:
                        if move == 'Д' and money >= bet:
                            bet *= 2  # Удваиваем ставку
                            bets[currentHandIndex] = bet
                            newCard = deck.pop()
                            messagesClear()
                            messages.append('Ставка увеличена до {}.'.format(bet))
                            screenUpdate()
                            playerHand.append(newCard)
                            # Сразу проверяем перебор
                            if getHandValue(playerHand) > 21:
                                break  # Перебор — сразу заканчиваем ход игрока
                            # После дабла спрашиваем, хочет ли игрок утроить:
                            if money >= initialBet:
                                move = ''
                                while (move != 'Y' and move != 'N'):
                                    screenUpdate('Утроение')
                                    for event in pygame.event.get():
                                        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonYes.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_y):
                                            move = 'Y'
                                        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonNo.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_n):
                                            move = 'N'
                                screenUpdate()
                                if move == 'Y':
                                    bet += initialBet  # Прибавляем начальную ставку
                                    bets[currentHandIndex] = bet
                                    newCard = deck.pop()
                                    messagesClear()
                                    messages.append('Ставка увеличена до {}.'.format(bet))
                                    playerHand.append(newCard)
                            break  # После дабл-дауна и трипл-дауна ход игрока заканчивается

                        if move in ('Х', 'Д'):
                            # "хит" или "дабл-даун": игрок берет еще одну карту.
                            newCard = deck.pop()
                            rank, suit = newCard
                            playerHand.append(newCard)

                            if getHandValue(playerHand) > 21:
                                # Перебор у игрока:
                                continue

                        if move in ('С', 'Д'):
                            # "стенд" или "дабл-даун": переход к следующей руке
                            break

                        if move == 'Р':
                            # Уже обработано выше
                            break

                    currentHandIndex += 1  # Переходим к следующей руке

                # Проверяем, есть ли хотя бы одна не сданная рука
                if all(surrendered):
                    continue  # Все руки сданы, пропускаем обработку дилера

            while True:  # Выполняем цикл до тех пор, пока игрок не скажет "хватит" или у него не будет перебор.
                # Проверка на перебор у игрока:
                if getHandValue(playerHand) > 21:
                    break

                # Получаем ход игрока: Х, С, О или Д:
                move = getMove(playerHand, money - sum(bets), len(playerHands) > 1)

                # Обработка отступных
                if move == 'О':
                    screenUpdate('Surrender')
                    surrendered[currentHandIndex] = True
                    surrenderAmount = bet // 2
                    messagesClear()
                    messages.append(f'Вы выбрали отступные. Возвращаем {surrenderAmount}')
                    screenUpdate()
                    money -= surrenderAmount
                    move = ''
                    while (move != 'Enter'):
                        screenUpdate('Enter')
                        for event in pygame.event.get():
                            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonEnter.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                                move = 'Enter'
                    screenUpdate(move)
                    break  # Завершаем текущую руку

                if (move == 'R'):
                    while (move != 'Enter'):
                        screenUpdate('R')
                        for event in pygame.event.get():
                            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonEnter.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                                move = 'Enter'
                    screenUpdate(move)

                # Игрок удваивает, он может увеличить ставку:
                if move == 'Д' and money >= bet:
                    bet *= 2  # Удваиваем ставку
                    bets[currentHandIndex] = bet
                    messagesClear()
                    messages.append('Ставка увеличена до {}.'.format(bet))
                    screenUpdate()
                    newCard = deck.pop()
                    playerHand.append(newCard)
                    # Сразу проверяем перебор
                    if getHandValue(playerHand) > 21:
                        break  # Перебор — сразу заканчиваем ход игрока
                    # После дабла спрашиваем, хочет ли игрок утроить:
                    if money >= initialBet:
                        move = ''
                        while (move != 'Y' and move != 'N'):
                            screenUpdate('Утроение')
                            for event in pygame.event.get():
                                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonYes.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_y):
                                    move = 'Y'
                                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonNo.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_n):
                                    move = 'N'
                        screenUpdate()
                        if move == 'Y':
                            bet += initialBet  # Прибавляем начальную ставку
                            bets[currentHandIndex] = bet
                            messagesClear()
                            messages.append('Ставка увеличена до {}.'.format(bet))
                            screenUpdate()
                            newCard = deck.pop()
                            playerHand.append(newCard)
                    break  # После дабл-дауна и трипл-дауна ход игрока заканчивается

                if move in ('Х', 'Д'):
                    # "хит" или "дабл-даун": игрок берет еще одну карту.
                    newCard = deck.pop()
                    rank, suit = newCard
                    playerHand.append(newCard)

                    if getHandValue(playerHand) > 21:
                        # Перебор у игрока:
                        continue

                if move in ('С', 'Д'):
                    # "стенд" или "дабл-даун": переход к следующей руке
                    break

                if move == 'Р':
                    # Уже обработано выше
                    break

            currentHandIndex += 1  # Переходим к следующей руке

        # Обработка действий дилера:
        if getHandValue(playerHand) <= 21:
            while getHandValue(dealerHand) < 17:
                # Дилер берет еще карту:
                messagesClear()
                messages.append('Дилер берет карту...')
                screenUpdate()
                dealerHand.append(deck.pop())
                showDealerHand = False

                if getHandValue(dealerHand) > 21:
                    break  # Перебор у дилера.
            messagesClear()
            messages.append('Нажмите Enter, чтобы продолжить...')
            screenUpdate()
            move = ''
            while (move != 'Enter'):
                screenUpdate('Enter')
                for event in pygame.event.get():
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonEnter.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                        move = 'Enter'
            screenUpdate(move)

        # Отображаем итоговые карты на руках:
        for i, playerHand in enumerate(playerHands):
            if surrendered[i]:
                continue  # Пропускаем сданные руки

            showDealerHand = True
            screenUpdate()

            playerValue = getHandValue(playerHand)
            dealerValue = getHandValue(dealerHand)
            bet = bets[i]
            i += 1

        playerValue = getHandValue(playerHand)
        dealerValue = getHandValue(dealerHand)
        # Проверяем, игрок выиграл, проиграл или сыграл вничью:
        message = ''
        screenUpdate()
        if dealerValue > 21:
            victory.play()
            message = 'Дилер проиграл! Вы выиграли ${}!'.format(bet)
            money += bet
            messagesClear()
            messages.append('Дилер проиграл! Вы выиграли ${}!'.format(bet))
            screenUpdate()
            move = ''
            while (move != 'Enter'):
                screenUpdate('End5')
                for event in pygame.event.get():
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonContinue.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                        move = 'Enter'
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonExit.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        sys.exit()
            screenUpdate()

        elif (playerValue > 21) or (playerValue < dealerValue):
            move = ''
            while (move != 'Enter'):
                screenUpdate('End2')
                for event in pygame.event.get():
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonContinue.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                        move = 'Enter'
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonExit.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        sys.exit()
            screenUpdate()
            money -= bet

        elif playerValue > dealerValue:
            messagesClear()
            victory.play()
            messages.append('Вы выиграли ${}!'.format(bet))
            screenUpdate()
            move = ''
            while (move != 'Enter'):
                screenUpdate('End3')
                for event in pygame.event.get():
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonContinue.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                        move = 'Enter'
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonExit.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        sys.exit()
            screenUpdate()

            money += bet
        elif playerValue == dealerValue:
            move = ''
            while (move != 'Enter'):
                screenUpdate('End4')
                for event in pygame.event.get():
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonContinue.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                        move = 'Enter'
                    if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonExit.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        sys.exit()
            screenUpdate()

        bet = 0
        screenUpdate()

        messagesClear()
        messages.append(message)
        messages.append('Нажмите Enter, чтобы продолжить...')
        screenUpdate()
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
    sprites.append(pygame.image.load("..\\Assets\\Money_bet.png"))
    sprites.append("Money_bet")
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
    pygame.mixer.music.load("..\\Sounds\\soundtrack.mp3")

def screenUpdate(moves = [], value = 0):
    global screen
    global dealerHand
    global showDealerHand
    global messages
    global money

    global buttonHit
    global buttonStand
    global buttonDouble
    global buttonEnter
    global buttonYes
    global buttonNo

    screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (1400, 1080)), (0, 0))
    screen.blit(pygame.transform.scale(sprites[sprites.index("Message_backround") - 1], (520, 1080)), (1400, 0))
    screen.blit(pygame.transform.scale(sprites[sprites.index("Field") - 1], (150, 140)), (80, 100))
    screen.blit(pygame.transform.scale(sprites[sprites.index("Money") - 1], (50, 50)), (220, 140))
    screen.blit(font.render('Деньги', True, (255, 255, 255)), (100, 100))
    screen.blit(font.render(money.__str__(), True, (255, 255, 255)), (105, 151))
    screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 140)), (1750, -45))
    if buttonExit.collidepoint(pygame.mouse.get_pos()):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (160, 150)), (1745, -50))
    screen.blit(font.render('Exit', True, (255, 255, 255)), (1800, 5))


    xPosition = 1450
    yPosition = 100

    i = 0
    while (i < 10 and i < len(messages)):
        screen.blit(fontMessage.render(messages[i], True, (255, 255, 255)), (xPosition, yPosition))
        yPosition += 50
        i += 1

    xPosition = 320
    yPosition = 150

    if (showDealerHand == True):
        screen.blit(fontPlayers.render('Дилер: ' + getHandValue(dealerHand).__str__(), True, (255, 255, 255)), (320, 100))
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
        screen.blit(fontPlayers.render('Дилер: ???', True, (255, 255, 255)), (320, 100))
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

    xPosition = 320
    yPosition = 340

    for h in range(0, len(playerHands)):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Field") - 1], (150, 140)), (80, yPosition))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Money_bet") - 1], (50, 50)), (220, yPosition + 40))
        screen.blit(font.render('Ставка ' + (h + 1).__str__(), True, (255, 255, 255)), (100, yPosition))
        screen.blit(font.render((bets[h]).__str__(), True, (255, 255, 255)), (100, yPosition + 51))
        currentHand = playerHands[h]
        screen.blit(fontPlayers.render('Игрок: ' + getHandValue(currentHand).__str__(), True, (255, 255, 255)), (320, yPosition - 40))
        for i in range(0, len(currentHand)):
            card = currentHand[i:(i+1)]
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
        xPosition = 320
        yPosition += 190


    screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (100, 100)), (1450, 800))
    screen.blit(fontMessage.render('(Х)ит', True, (255, 255, 255)), (1483, 839))
    screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (100, 100)), (1550, 800))
    screen.blit(fontMessage.render('(С)тенд', True, (255, 255, 255)), (1576, 839))
    screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (100, 100)), (1650, 800))
    screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (100, 100)), (1750, 800))
    screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (100, 100)), (1450, 900))
    screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (100, 100)), (1550, 900))
    screen.blit(fontMessage.render('Правила', True, (255, 255, 255)), (1573, 939))

    if ('Surrender' in moves):
        screen.blit(fontMessage.render('Отступные', True, (255, 255, 255)), (1467, 939))

    if ('Surrender' not in moves):
        screen.blit(fontMessage.render('', True, (255, 255, 255)), (1467, 939))

    if ('(Д)абл-даун' in moves):
        screen.blit(fontMessage.render('(Д)абл-даун', True, (255, 255, 255)), (1664, 839))

    if ('(Д)абл-даун' not in moves):
        screen.blit(fontMessage.render('', True, (255, 255, 255)), (1664, 839))

    if ('Enter' in moves):
        screen.blit(fontMessage.render('Enter', True, (255, 255, 255)), (1784, 839))

    if ('Enter' not in moves):
        screen.blit(fontMessage.render('Enter', True, (255, 255, 255)), (1784, 839))

    if buttonHit.collidepoint(pygame.mouse.get_pos()):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (110, 110)), (1445, 795))
        screen.blit(fontMessage.render('(Х)ит', True, (255, 255, 255)), (1483, 839))

    if buttonStand.collidepoint(pygame.mouse.get_pos()):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (110, 110)), (1545, 795))
        screen.blit(fontMessage.render('(С)тенд', True, (255, 255, 255)), (1576, 839))

    if buttonRules.collidepoint(pygame.mouse.get_pos()):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (110, 110)), (1545, 895))
        screen.blit(fontMessage.render('Правила', True, (255, 255, 255)), (1573, 939))

    if buttonSurrender.collidepoint(pygame.mouse.get_pos()) and 'Surrender' in moves:
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (110, 110)), (1445, 895))
        screen.blit(fontMessage.render('Отступные', True, (255, 255, 255)), (1467, 939))

    if buttonDouble.collidepoint(pygame.mouse.get_pos()) and '(Д)абл-даун' in moves:
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (110, 110)), (1645, 795))
        screen.blit(fontMessage.render('(Д)абл-даун', True, (255, 255, 255)), (1664, 839))

    if buttonEnter.collidepoint(pygame.mouse.get_pos()) and 'Enter' in moves:
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (110, 110)), (1745, 795))
        screen.blit(fontMessage.render('Enter', True, (255, 255, 255)), (1784, 839))

    if ('R' in moves):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (1200, 800)), (450, 200))
        screen.blit(font.render("Правила", True, (255, 255, 255)), (1000, 300))
        screen.blit(font.render("Постарайтесь набрать как можно больше очков, не превышая 21.", True,  (255, 255, 255)), (560, 350))
        screen.blit(font.render("Короли, дамы и валеты стоят 10 очков.", True, (255, 255, 255)),(560, 400))
        screen.blit(font.render("Тузы может быть 1 или 11 очков.", True, (255, 255, 255)),(560, 450))
        screen.blit(font.render("Карты со 2 по 10 стоят по их номиналу.", True, (255, 255, 255)),(560, 500))
        screen.blit(font.render("(Х)ит - чтобы взять еще карту.", True, (255, 255, 255)),(560, 550))
        screen.blit(font.render("(С)тенд - чтобы перестать брать карты.", True, (255, 255, 255)),(560, 600))
        screen.blit(font.render("В первой игре вы можете сделать (Д)абл-даун, чтобы увеличить свою ставку,", True, (255, 255, 255)),(560, 650))
        screen.blit(font.render("но вы получите ровно одну карту.", True, (255, 255, 255)),(560, 700))
        screen.blit(font.render("В случае ничьей ставка возвращается игроку.", True, (255, 255, 255)),(560, 750))
        screen.blit(font.render("Дилер прекращает брать карты после 17 очков.", True, (255, 255, 255)),(560, 800))
        screen.blit(font.render("Нажмите Enter чтобы закрыть данное меню", True, (255, 255, 255)), (560, 850))

    if ('Ставка' in moves):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render("Введите ставку", True, (255, 255, 255)), (760, 500))
        screen.blit(font.render(value.__str__(), True,  (255, 255, 255)), (760, 550))

    if ('Равные деньги' in moves):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render('Хотите получить "равные деньги"?', True, (255, 255, 255)), (640, 500))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (690, 550))
        if buttonYes.collidepoint(pygame.mouse.get_pos()):
            screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (160, 160)), (685, 545))
        screen.blit(fontPlayers.render('Да', True, (255, 255, 255)), (752, 607))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (880, 550))
        if buttonNo.collidepoint(pygame.mouse.get_pos()):
            screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (160, 160)), (875, 545))
        screen.blit(fontPlayers.render('Нет', True, (255, 255, 255)), (930, 607))

    if ('Утроение' in moves):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render('Хотите утроить ставку?', True, (255, 255, 255)), (705, 470))
        screen.blit(font.render('и взять еще одну карту?', True, (255, 255, 255)), (705, 520))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (690, 550))
        if buttonYes.collidepoint(pygame.mouse.get_pos()):
            screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (160, 160)), (685, 545))
        screen.blit(fontPlayers.render('Да', True, (255, 255, 255)), (752, 607))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (880, 550))
        if buttonNo.collidepoint(pygame.mouse.get_pos()):
            screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (160, 160)), (875, 545))
        screen.blit(fontPlayers.render('Нет', True, (255, 255, 255)), (930, 607))

    if ('Страховка' in moves):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render('Хотите получить страховку?', True, (255, 255, 255)), (680, 500))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (690, 550))
        if buttonYes.collidepoint(pygame.mouse.get_pos()):
            screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (160, 160)), (685, 545))
        screen.blit(fontPlayers.render('Да', True, (255, 255, 255)), (752, 607))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (880, 550))
        if buttonNo.collidepoint(pygame.mouse.get_pos()):
            screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (160, 160)), (875, 545))
        screen.blit(fontPlayers.render('Нет', True, (255, 255, 255)), (930, 607))

    if ('Разбиение' in moves):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render('Доступно разбиение', True, (255, 255, 255)), (720, 500))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (690, 550))
        if buttonYes.collidepoint(pygame.mouse.get_pos()):
            screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (160, 160)), (685, 545))
        screen.blit(fontPlayers.render('Да', True, (255, 255, 255)), (752, 607))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (880, 550))
        if buttonNo.collidepoint(pygame.mouse.get_pos()):
            screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (160, 160)), (875, 545))
        screen.blit(fontPlayers.render('Нет', True, (255, 255, 255)), (930, 607))

    if ('End' in moves and buttonEnd.collidepoint(pygame.mouse.get_pos()) == 0 and buttonContinue.collidepoint(pygame.mouse.get_pos()) == 0):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render("Игра окончена. Вы проиграли", True, (255, 255, 255)), (670, 500))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (880, 550))
        screen.blit(fontMessage.render("Заново", True, (255, 255, 255)), (927, 615))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (690, 550))
        screen.blit(fontMessage.render("Выйти", True, (255, 255, 255)), (745, 615))

    if ('End' in moves and buttonEnd.collidepoint(pygame.mouse.get_pos()) == 1 and buttonContinue.collidepoint(pygame.mouse.get_pos()) == 0):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render("Игра окончена. Вы проиграли", True, (255, 255, 255)), (670, 500))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (880, 550))
        screen.blit(fontMessage.render("Заново", True, (255, 255, 255)), (927, 615))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (160, 160)), (685, 545))
        screen.blit(fontMessage.render("Выйти", True, (255, 255, 255)), (745, 615))

    if ('End' in moves and buttonEnd.collidepoint(pygame.mouse.get_pos()) == 0 and buttonContinue.collidepoint(pygame.mouse.get_pos()) == 1):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render("Игра окончена. Вы проиграли", True, (255, 255, 255)), (670, 500))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (160, 160)), (875, 545))
        screen.blit(fontMessage.render("Заново", True, (255, 255, 255)), (927, 615))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (690, 550))
        screen.blit(fontMessage.render("Выйти", True, (255, 255, 255)), (745, 615))

    if ('End2' in moves and buttonEnd.collidepoint(pygame.mouse.get_pos()) == 0 and buttonContinue.collidepoint(pygame.mouse.get_pos()) == 0):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render("Вы проиграли этот раунд", True, (255, 255, 255)), (700, 500))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (880, 550))
        screen.blit(fontMessage.render("Продолжить", True, (255, 255, 255)), (917, 615))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (690, 550))
        screen.blit(fontMessage.render("Выйти", True, (255, 255, 255)), (745, 615))

    if ('End2' in moves and buttonEnd.collidepoint(pygame.mouse.get_pos()) == 1 and buttonContinue.collidepoint(pygame.mouse.get_pos()) == 0):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render("Вы проиграли этот раунд", True, (255, 255, 255)), (700, 500))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (880, 550))
        screen.blit(fontMessage.render("Продолжить", True, (255, 255, 255)), (917, 615))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (160, 160)), (685, 545))
        screen.blit(fontMessage.render("Выйти", True, (255, 255, 255)), (745, 615))

    if ('End2' in moves and buttonEnd.collidepoint(pygame.mouse.get_pos()) == 0 and buttonContinue.collidepoint(pygame.mouse.get_pos()) == 1):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render("Вы проиграли этот раунд", True, (255, 255, 255)), (700, 500))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (160, 160)), (875, 545))
        screen.blit(fontMessage.render("Продолжить", True, (255, 255, 255)), (917, 615))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (690, 550))
        screen.blit(fontMessage.render("Выйти", True, (255, 255, 255)), (745, 615))

    if ('End3' in moves and buttonEnd.collidepoint(pygame.mouse.get_pos()) == 0 and buttonContinue.collidepoint(pygame.mouse.get_pos()) == 0):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render("Вы выиграли этот раунд", True, (255, 255, 255)), (700, 500))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (880, 550))
        screen.blit(fontMessage.render("Продолжить", True, (255, 255, 255)), (917, 615))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (690, 550))
        screen.blit(fontMessage.render("Выйти", True, (255, 255, 255)), (745, 615))

    if ('End3' in moves and buttonEnd.collidepoint(pygame.mouse.get_pos()) == 1 and buttonContinue.collidepoint(pygame.mouse.get_pos()) == 0):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render("Вы выиграли этот раунд", True, (255, 255, 255)), (700, 500))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (880, 550))
        screen.blit(fontMessage.render("Продолжить", True, (255, 255, 255)), (917, 615))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (160, 160)), (685, 545))
        screen.blit(fontMessage.render("Выйти", True, (255, 255, 255)), (745, 615))

    if ('End3' in moves and buttonEnd.collidepoint(pygame.mouse.get_pos()) == 0 and buttonContinue.collidepoint(pygame.mouse.get_pos()) == 1):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render("Вы выиграли этот раунд", True, (255, 255, 255)), (700, 500))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (160, 160)), (875, 545))
        screen.blit(fontMessage.render("Продолжить", True, (255, 255, 255)), (917, 615))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (690, 550))
        screen.blit(fontMessage.render("Выйти", True, (255, 255, 255)), (745, 615))

    if ('End4' in moves and buttonEnd.collidepoint(pygame.mouse.get_pos()) == 0 and buttonContinue.collidepoint(pygame.mouse.get_pos()) == 0):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render("В этом раунде ничья", True, (255, 255, 255)), (730, 500))
        screen.blit(font.render("Ставка возвращена", True, (255, 255, 255)), (730, 550))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (880, 550))
        screen.blit(fontMessage.render("Продолжить", True, (255, 255, 255)), (917, 615))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (690, 550))
        screen.blit(fontMessage.render("Выйти", True, (255, 255, 255)), (745, 615))

    if ('End4' in moves and buttonEnd.collidepoint(pygame.mouse.get_pos()) == 1 and buttonContinue.collidepoint(pygame.mouse.get_pos()) == 0):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render("В этом раунде ничья", True, (255, 255, 255)), (730, 500))
        screen.blit(font.render("Ставка возвращена", True, (255, 255, 255)), (730, 550))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (880, 550))
        screen.blit(fontMessage.render("Продолжить", True, (255, 255, 255)), (917, 615))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (160, 160)), (685, 545))
        screen.blit(fontMessage.render("Выйти", True, (255, 255, 255)), (745, 615))

    if ('End4' in moves and buttonEnd.collidepoint(pygame.mouse.get_pos()) == 0 and buttonContinue.collidepoint(pygame.mouse.get_pos()) == 1):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render("В этом раунде ничья", True, (255, 255, 255)), (730, 500))
        screen.blit(font.render("Ставка возвращена", True, (255, 255, 255)), (730, 550))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (160, 160)), (875, 545))
        screen.blit(fontMessage.render("Продолжить", True, (255, 255, 255)), (917, 615))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (690, 550))
        screen.blit(fontMessage.render("Выйти", True, (255, 255, 255)), (745, 615))

    if ('End5' in moves and buttonEnd.collidepoint(pygame.mouse.get_pos()) == 0 and buttonContinue.collidepoint(pygame.mouse.get_pos()) == 0):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render("Дилер проиграл", True, (255, 255, 255)), (750, 450))
        screen.blit(font.render("Ставка возвращена", True, (255, 255, 255)), (730, 500))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (880, 550))
        screen.blit(fontMessage.render("Продолжить", True, (255, 255, 255)), (917, 615))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (690, 550))
        screen.blit(fontMessage.render("Выйти", True, (255, 255, 255)), (745, 615))

    if ('End5' in moves and buttonEnd.collidepoint(pygame.mouse.get_pos()) == 1 and buttonContinue.collidepoint(pygame.mouse.get_pos()) == 0):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render("Дилер проиграл", True, (255, 255, 255)), (750, 450))
        screen.blit(font.render("Ставка возвращена", True, (255, 255, 255)), (730, 500))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (880, 550))
        screen.blit(fontMessage.render("Продолжить", True, (255, 255, 255)), (917, 615))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (160, 160)), (685, 545))
        screen.blit(fontMessage.render("Выйти", True, (255, 255, 255)), (745, 615))

    if ('End5' in moves and buttonEnd.collidepoint(pygame.mouse.get_pos()) == 0 and buttonContinue.collidepoint(pygame.mouse.get_pos()) == 1):
        screen.blit(pygame.transform.scale(sprites[sprites.index("Backround") - 1], (500, 300)), (600, 400))
        screen.blit(font.render("Дилер проиграл", True, (255, 255, 255)), (750, 450))
        screen.blit(font.render("Ставка возвращена", True, (255, 255, 255)), (730, 500))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (160, 160)), (875, 545))
        screen.blit(fontMessage.render("Продолжить", True, (255, 255, 255)), (917, 615))
        screen.blit(pygame.transform.scale(sprites[sprites.index("Button") - 1], (150, 150)), (690, 550))
        screen.blit(fontMessage.render("Выйти", True, (255, 255, 255)), (745, 615))

    pygame.display.flip()

def messagesClear():
    global messages
    if (len(messages) > 10):
        messages.clear()

def getBet(maxBet):
    value = ""
    """Спрашиваем у игрока, сколько он ставит на этот раунд."""
    while True:  # Продолжаем спрашивать, пока не будет введено допустимое значение.
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

def getMove(playerHand, money, can_split=False):
    global buttonHit
    """Спрашиваем, какой ход хочет сделать игрок, и возвращаем 'Х', если он
    хочет взять еще карту, 'С', если ему хватит, и 'Д', если он удваивает."""
    while True:  # Продолжаем итерации цикла, пока игрок не сделает допустимый ход.
        # Определяем, какие ходы может сделать игрок:
        moves = ['(Х)ит', '(С)тенд', 'Surrender']

        # Игрок может удвоить при первом ходе, это ясно из того,
        # что у игрока ровно две карты:
        if len(playerHand) == 2 and money > 0:
            moves.append('(Д)абл-даун')

        # Получаем ход игрока:
        screenUpdate(moves)
        move = 'q'
        while (move == 'q'):
            screenUpdate(moves)
            for event in pygame.event.get():
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonHit.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_x):
                    move = 'Х'
                    cardFlick.play()
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonStand.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_c):
                    move = 'С'
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonDouble.collidepoint(pygame.mouse.get_pos()) and '(Д)абл-даун' in moves) or (event.type == pygame.KEYDOWN and event.key == pygame.K_d  and '(Д)абл-даун' in moves):
                    move = 'Д'
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonSurrender.collidepoint(pygame.mouse.get_pos()) and '(Д)абл-даун' in moves) or (event.type == pygame.KEYDOWN and event.key == pygame.K_o):
                    move = 'О'
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonExit.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    sys.exit()
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and buttonRules.collidepoint(pygame.mouse.get_pos())) or (event.type == pygame.KEYDOWN and event.key == pygame.K_r):
                    move = 'R'
        screenUpdate(moves)
        if move in ('Х', 'С', 'О', 'R'):
            return move  # Игрок сделал допустимый ход.
        if move == 'Д' and '(Д)абл-даун' in moves:
            return move  # Игрок сделал допустимый ход.

def canSplit(hand):
    """Проверяет, можно ли разбить руку (две карты одного достоинства)."""
    if len(hand) != 2:
        return False
    rank1, _ = hand[0]
    rank2, _ = hand[1]

    # Все картинки (J, Q, K) считаются одинаковыми для сплита
    if rank1 in ('J', 'Q', 'K') and rank2 in ('J', 'Q', 'K'):
        return True
    return rank1 == rank2

# Если программа не импортируется, а запускается, производим запуск:
if __name__ == '__main__':
   main()