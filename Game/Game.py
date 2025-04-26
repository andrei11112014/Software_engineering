import random, sys

# Задаем значения констант:
HEARTS = chr(9829)
DIAMONDS = chr(9830)
SPADES = chr(9824)
CLUBS = chr(9827)
BACKSIDE = 'backside'


def main():
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
            displayHands(playerHand, dealerHand, False)

            playerHasBlackjack = getHandValue(playerHand) == 21
            if playerHasBlackjack:
                print('Дилер раскрывает туз, и у вас в руках блэкджек!')
                print('"Равные деньги" — это страховка 1:1 вместо стандартных 3:2.')
                choice = input('Хотите получить "равные деньги"? (ДА/НЕТ)').upper()
                if choice == 'ДА':
                    evenMoneyTaken = True
                    print('Вы взяли "равные деньги". Выигрыш:', bet)
                    money += bet  # Выплата 1:1 сразу
            else:
                print('У дилера туз. Доступна страховка (половина от первоначальной ставки).')
                choice = input('Хотите получить страховку? (ДА/НЕТ)').upper()
                if choice == 'ДА':
                    insuranceBet = bet // 2
                    print(f'Страховка: {insuranceBet}')
                    money -= insuranceBet

        # Проверяем блэкджек у дилера
        dealerHasBlackjack = getHandValue(dealerHand) == 21

        if dealerHasBlackjack:
            displayHands(playerHand, dealerHand, True)

            playerHasBlackjack = getHandValue(playerHand) == 21

            if playerHasBlackjack:
                if not evenMoneyTaken:
                    print('И у вас, и у дилера блэкджек! Ничья!')
                    money += bet  # Возвращаем ставку
            else:
                print('У дилера блэкджек! Вы проиграли ставку.')
                money -= bet

                if insuranceBet > 0:
                    print('Но вы выиграли страховку! Выплата 2:1.')
                    money += insuranceBet * 3  # +3 потому что 2:1 от страховки + возврат самой страховки

            input('Нажмите Enter, чтобы продолжить...')
            print('\n\n')
            continue

        elif insuranceBet > 0:
            print('У дилера нет блэкджека. Вы потеряли страховку.')
            # Страховка уже вычтена ранее
            input('Нажмите Enter, чтобы продолжить...')
            print('\n\n')

        # Если игрок взял even money - пропускаем основной раунд
        if evenMoneyTaken:
            input('Нажмите Enter, чтобы продолжить...')
            print('\n\n')
            continue

        # Обработка действий игрока:
        print('Ставка:', bet)
        initialBet = bet  # Сохраняем первоначальную ставку
        while True:  # Выполняем цикл до тех пор, пока игрок не скажет "хватит" или у него не будет перебор.
            displayHands(playerHand, dealerHand, False)
            print()

            # Проверка на перебор у игрока:
            if getHandValue(playerHand) > 21:
                break

            # Получаем ход игрока: Х, С или Д:
            move = getMove(playerHand, money - bet)

            
            # Игрок удваивает, он может увеличить ставку:
            if move == 'Д' and money >= bet:
                bet *= 2  # Удваиваем ставку
                print('Ставка увеличена до {}.'.format(bet))
                newCard = deck.pop()
                print('Вы получили {} из {}.'.format(newCard[0], newCard[1]))
                playerHand.append(newCard)
                displayHands(playerHand, dealerHand, False)
                # Сразу проверяем перебор
                if getHandValue(playerHand) > 21:
                    break  # Перебор — сразу заканчиваем ход игрока
                # После дабла спрашиваем, хочет ли игрок утроить:
                if money >= initialBet:
                    choice = input('Хотите утроить ставку и взять еще одну карту? (ДА/НЕТ) ').upper()
                    if choice == 'ДА':
                        bet += initialBet  # Прибавляем начальную ставку
                        print('Ставка увеличена до {}.'.format(bet))
                        newCard = deck.pop()
                        print('Вы получили {} из {}.'.format(newCard[0], newCard[1]))
                        playerHand.append(newCard)
                        displayHands(playerHand, dealerHand, False)
                break  # После дабл-дауна и трипл-дауна ход игрока заканчивается

            if move in ('Х', 'Д'):
                # "хит" или "дабл-даун": игрок берет еще одну карту.
                newCard = deck.pop()
                rank, suit = newCard
                print('Вы получили {} из {}.'.format(rank, suit))
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
                dealerHand.append(deck.pop())
                displayHands(playerHand, dealerHand, False)

                if getHandValue(dealerHand) > 21:
                    break  # Перебор у дилера.
            input('Нажмите Enter, чтобы продолжить...')
            print('\n\n')

        # Отображаем итоговые карты на руках:
        displayHands(playerHand, dealerHand, True)

        playerValue = getHandValue(playerHand)
        dealerValue = getHandValue(dealerHand)
        # Проверяем, игрок выиграл, проиграл или сыграл вничью:
        if dealerValue > 21:
            print('Дилер проиграл! Вы выиграли ${}!'.format(bet))
            money += bet
        elif (playerValue > 21) or (playerValue < dealerValue):
            print('Вы проиграли!')
            money -= bet
        elif playerValue > dealerValue:
            print('Вы выиграли ${}!'.format(bet))
            money += bet
        elif playerValue == dealerValue:
            print('Ничья, ставка возвращена.')

        input('Нажмите Enter, чтобы продолжить...')
        print('\n\n')


def getBet(maxBet):
    """Спрашиваем у игрока, сколько он ставит на этот раунд."""
    while True:  # Продолжаем спрашивать, пока не будет введено допустимое значение.
        print('Сколько вы ставите? (1-{}, or ВЫХОД)'.format(maxBet))
        bet = input('> ').upper().strip()
        if bet == 'ВЫХОД':
            print('Спасибо за игру!')
            sys.exit()

        if not bet.isdecimal():
            continue  # Если игрок не ответил — спрашиваем снова.

        bet = int(bet)
        if 1 <= bet <= maxBet:
            return bet  # Игрок ввел допустимое значение ставки.


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
        move = input(movePrompt).upper()
        if move in ('Х', 'С'):
            return move  # Игрок сделал допустимый ход.
        if move == 'Д' and '(Д)абл-даун' in moves:
            return move  # Игрок сделал допустимый ход.


# Если программа не импортируется, а запускается, производим запуск:
if __name__ == '__main__':
    main()
