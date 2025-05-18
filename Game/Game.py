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
  Тузы могут стоить 1 или 11 очков.
  Карты со 2 по 10 стоят по их номиналу.
  (Х)ит - чтобы взять еще карту.
  (С)тенд - чтобы перестать брать карты.
  (О)тступные - сдать половину ставки, если у вас плохие карты.
  В первой игре вы можете сделать (Д)абл-даун, чтобы увеличить свою ставку,
  но вы получите ровно одну карту.
  После дабл-дауна можно утроить ставку, взяв еще одну карту.
  Если у вас две карты одного достоинства, можно (Р)азбить пару на две руки.
  Важно: После взятия карты вы не можете от нее отказаться.
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
        playerHands = [[deck.pop(), deck.pop()]]  # Теперь это список рук игрока
        currentHandIndex = 0
        bets = [bet]  # Список ставок для каждой руки
        insuranceBets = [0]  # Список страховок для каждой руки
        evenMoneyTaken = False
        surrendered = [False]  # Список флагов отступных для каждой руки

        # Проверяем возможность страховки/равных денег
        if dealerHand[0][0] == 'A':  # Если у дилера туз
            displayHands(playerHands[currentHandIndex], dealerHand, False)

            playerHasBlackjack = getHandValue(playerHands[currentHandIndex]) == 21
            if playerHasBlackjack:
                print('Дилер раскрывает туз, и у вас в руках блэкджек!')
                print('"Равные деньги" — это страховка 1:1 вместо стандартных 3:2.')
                choice = input('Хотите получить "равные деньги"? (ДА/НЕТ)').upper()
                if choice == 'ДА':
                    evenMoneyTaken = True
                    print('Вы взяли "равные деньги". Выигрыш:', bets[currentHandIndex])
                    money += bets[currentHandIndex]  # Выплата 1:1 сразу
            else:
                print('У дилера туз. Доступна страховка (половина от первоначальной ставки).')
                choice = input('Хотите получить страховку? (ДА/НЕТ)').upper()
                if choice == 'ДА':
                    insuranceBets[currentHandIndex] = bets[currentHandIndex] // 2
                    print(f'Страховка: {insuranceBets[currentHandIndex]}')
                    money -= insuranceBets[currentHandIndex]

        # Проверяем блэкджек у дилера
        dealerHasBlackjack = getHandValue(dealerHand) == 21

        if dealerHasBlackjack:
            displayHands(playerHands[currentHandIndex], dealerHand, True)

            playerHasBlackjack = getHandValue(playerHands[currentHandIndex]) == 21

            if playerHasBlackjack:
                if not evenMoneyTaken:
                    print('И у вас, и у дилера блэкджек! Ничья!')
                    money += bets[currentHandIndex]  # Возвращаем ставку
            else:
                print('У дилера блэкджек! Вы проиграли ставку.')
                money -= bets[currentHandIndex]

                if insuranceBets[currentHandIndex] > 0:
                    print('Но вы выиграли страховку! Выплата 2:1.')
                    money += insuranceBets[currentHandIndex] * 3  # +3 потому что 2:1 от страховки + возврат самой страховки

            input('Нажмите Enter, чтобы продолжить...')
            print('\n\n')
            continue

        elif insuranceBets[currentHandIndex] > 0:
            print('У дилера нет блэкджека. Вы потеряли страховку.')
            # Страховка уже вычтена ранее
            input('Нажмите Enter, чтобы продолжить...')
            print('\n\n')

        # Если игрок взял even money - пропускаем основной раунд
        if evenMoneyTaken:
            input('Нажмите Enter, чтобы продолжить...')
            print('\n\n')
            continue

        # Обработка всех рук игрока
        while currentHandIndex < len(playerHands):
            playerHand = playerHands[currentHandIndex]
            bet = bets[currentHandIndex]
            initialBet = bet  # Сохраняем первоначальную ставку для текущей руки

            # Проверяем возможность сплита
            if len(playerHand) == 2 and canSplit(playerHand) and money >= bet:
                rank1, _ = playerHand[0]
                rank2, _ = playerHand[1]
                if rank1 == rank2:
                    print(f'У вас пара {rank1}. Можно разбить руку.')
                    move = getMove(playerHand, money - sum(bets), can_split=True)
                    if move == 'Р':
                        # Вычитаем дополнительную ставку
                        money -= bet
                        bets.append(bet)
                        insuranceBets.append(0)
                        surrendered.append(False)

                        # Разбиваем руку
                        newHand1 = [playerHand[0], deck.pop()]
                        newHand2 = [playerHand[1], deck.pop()]

                        # Заменяем текущую руку и добавляем новую
                        playerHands[currentHandIndex] = newHand1
                        playerHands.insert(currentHandIndex + 1, newHand2)

                        # Показываем новые руки
                        print('\nПервая рука после сплита:')
                        displayHands(newHand1, dealerHand, False)
                        print('\nВторая рука после сплита:')
                        displayHands(newHand2, dealerHand, False)
                        input('Нажмите Enter, чтобы продолжить...')

                        # Переходим к обработке первой руки после сплита
                        continue

            # Обработка действий для текущей руки:
            print(f'\nОбрабатывается рука {currentHandIndex + 1} из {len(playerHands)}')
            print('Ставка:', bet)

            while True:  # Выполняем цикл до тех пор, пока игрок не скажет "хватит" или у него не будет перебор.
                displayHands(playerHand, dealerHand, False)
                print()

                # Проверка на перебор у игрока:
                if getHandValue(playerHand) > 21:
                    break

                # Получаем ход игрока: Х, С, О или Д:
                move = getMove(playerHand, money - sum(bets), len(playerHands) > 1)

                # Обработка отступных
                if move == 'О':
                    surrendered[currentHandIndex] = True
                    surrenderAmount = bet // 2
                    print(f'Вы выбрали отступные. Возвращаем {surrenderAmount}')
                    money -= surrenderAmount
                    input('Нажмите Enter, чтобы продолжить...')
                    print('\n\n')
                    break # Завершаем текущую руку

                # Игрок удваивает, он может увеличить ставку:
                if move == 'Д' and money >= bet:
                    bet *= 2  # Удваиваем ставку
                    bets[currentHandIndex] = bet
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
                            bets[currentHandIndex] = bet
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
                    # "стенд" или "дабл-даун": переход к следующей руке
                    break

                if move == 'Р':
                    # Уже обработано выше
                    break

            currentHandIndex += 1  # Переходим к следующей руке

        # Проверяем, есть ли хотя бы одна не сданная рука
        if all(surrendered):
            continue  # Все руки сданы, пропускаем обработку дилера

        # Обработка действий дилера:
        dealerValue = getHandValue(dealerHand)
        for i, playerHand in enumerate(playerHands):
            if surrendered[i]:
                continue  # Пропускаем сданные руки

            playerValue = getHandValue(playerHand)
            if playerValue > 21:
                continue  # Перебор, дилеру не нужно играть

            while dealerValue < 17:
                # Дилер берет еще карту:
                print('Дилер берет карту...')
                dealerHand.append(deck.pop())
                dealerValue = getHandValue(dealerHand)
                displayHands(playerHand, dealerHand, False)

                if dealerValue > 21:
                    break  # Перебор у дилера.

        input('Нажмите Enter, чтобы продолжить...')
        print('\n\n')

        # Отображаем итоговые карты на руках:
        for i, playerHand in enumerate(playerHands):
            if surrendered[i]:
                continue  # Пропускаем сданные руки

            print(f'\nРезультаты для руки {i + 1}:')
            displayHands(playerHand, dealerHand, True)

            playerValue = getHandValue(playerHand)
            dealerValue = getHandValue(dealerHand)
            bet = bets[i]

            # Проверяем, игрок выиграл, проиграл или сыграл вничью:
            if playerValue > 21:
                print('Перебор! Вы проиграли ставку для этой руки.')
                money -= bet
            elif dealerValue > 21:
                print('Дилер проиграл! Вы выиграли ${}!'.format(bet))
                money += bet
            elif playerValue < dealerValue:
                print('Вы проиграли ставку для этой руки!')
                money -= bet
            elif playerValue > dealerValue:
                print('Вы выиграли ${}!'.format(bet))
                money += bet
            elif playerValue == dealerValue:
                print('Ничья, ставка возвращена.')
                # money остается без изменений

        input('Нажмите Enter, чтобы продолжить...')
        print('\n\n')


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


def getMove(playerHand, money, can_split=False):
    """Спрашиваем, какой ход хочет сделать игрок, и возвращаем 'Х', если он
    хочет взять еще карту, 'С', если ему хватит, 'О' для отступных, 'Д' если он удваивает,
    и 'Р' если он разбивает пару."""
    while True:  # Продолжаем итерации цикла, пока игрок не сделает допустимый ход.
        # Определяем, какие ходы может сделать игрок:
        moves = ['(Х)ит', '(С)тенд']

        # Игрок может сделать отступные только при первом ходе (2 карты)
        if len(playerHand) == 2:
            moves.append('(О)тступные')

        # Игрок может удвоить при первом ходе, это ясно из того,
        # что у игрока ровно две карты:
        if len(playerHand) == 2 and money > 0:
            moves.append('(Д)абл-даун')

        # Игрок может разбить пару, если у него две карты одного достоинства
        # и достаточно денег для дополнительной ставки
        if can_split and len(playerHand) == 2 and money > 0:
            moves.append('(Р)азбить пару')

        print('Вы не можете отказаться от уже взятых карт!')
        # Получаем ход игрока:
        movePrompt = ', '.join(moves) + '> '
        move = input(movePrompt).upper()
        if move in ('Х', 'С'):
            return move  # Игрок сделал допустимый ход.
        if move == 'О' and '(О)тступные' in moves:
            return move  # Игрок выбрал отступные
        if move == 'Д' and '(Д)абл-даун' in moves:
            return move  # Игрок сделал допустимый ход.
        if move == 'Р' and '(Р)азбить пару' in moves:
            return move  # Игрок выбрал разбиение пары


# Если программа не импортируется, а запускается, производим запуск:
if __name__ == '__main__':
    main()
