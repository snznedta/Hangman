from django.shortcuts import render, redirect

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

# Django transaction system so we can use @transaction.atomic
from django.db import transaction

from hangman.models import Game

import random
from datetime import datetime
from random import choice
import logging

logger_format = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('hangman')
logger.setLevel(logging.INFO)

dic = []


def load_dict():
    with open("hangman/words.txt") as words:
        for word in words:
            dic.append(word.strip().lower())


def get_word():
    if len(dic) == 0:
        load_dict()
        return get_word()
    else:
        random.seed(datetime.now())
        return choice(dic)


@login_required
def home(request):
    return redirect('/hangman/game')


@login_required
def start_game(request):
    if request.method == 'GET':
        word = get_word()
        game = Game(user=request.user, answer=word)
        game.save()
        logger.info("starting new game %s for user:" % request.user)
        game.image = "/static/images/hang0.gif"
        game.display = "_ " * len(word)
        return render(request, "hangman.html", {'guessed': [], "game": game})
    else:
        return button(request)


@login_required
def button(request):
    game_id = int(request.POST['game_id'])

    game = Game.objects.get(game_id=game_id)
    # avoid user change message
    if game.user != request.user:
        return render(request, "hangman.html")
    answer = game.answer

    cur_guess = request.POST['letter']
    guessed = list(game.guessed)

    if game.status == "win" or game.status == "lose":
        generate_finished_game(game)
        return render(request, "hangman.html", {'guessed': guessed, 'game': game})
    if cur_guess not in guessed:
        guessed.append(cur_guess)
        game.guessed = "".join(guessed)
        game.save()
    word_to_display = ""

    match_num = 0
    for char in answer:
        if char in guessed:
            match_num += 1
            word_to_display += char + ' '
        else:
            word_to_display += '_ '

    if match_num == len(answer):
        game.status = "win"
        game.save()
    game.display = word_to_display

    num_wrong_guess = 0
    for char in guessed:
        if char not in answer:
            num_wrong_guess += 1
    if num_wrong_guess >= 10:
        game.status = 'lose'
        game.save()
        num_wrong_guess = 10
    game.image = "/static/images/hang" + str(num_wrong_guess) + ".gif"

    return render(request, "hangman.html", {'guessed': guessed, 'game': game})


def generate_finished_game(game):
    answer = game.answer
    guessed = list(game.guessed)
    if game.status == "win":
        game.display = " ".join(list(answer))
        game.image = "/static/images/hang" + str(wrong_num(guessed, answer)) + ".gif"
        return
    else:
        game.display = word_to_display(guessed, answer)
        game.image = "/static/images/hang10.gif"
        return


def wrong_num(guessed, answer):
    num_wrong_guess = 0
    for char in guessed:
        if char not in answer:
            num_wrong_guess += 1
    if num_wrong_guess >= 10:
        num_wrong_guess = 10
    return num_wrong_guess


def word_to_display(guessed, answer):
    display = ""
    match_num = 0
    for char in answer:
        if char in guessed:
            match_num += 1
            display += char + " "
        else:
            display += '_ '
    return display


@transaction.atomic
def register(request):
    context = {}
    errors = []
    context['errors'] = errors

    # Just display the registration form if this is a GET request
    if request.method == 'GET':
        return render(request, 'register.html', context)

    if User.objects.select_for_update().filter(username=request.POST['username']).exists():
        errors.append('Username is already taken.')
        return render(request, 'register.html', context)

    new_user = User.objects.create_user(username=request.POST['username'],
                                        password=request.POST['password'],
                                        first_name=request.POST['firstname'],
                                        last_name=request.POST['lastname'])
    new_user.save()
    new_user = authenticate(username=request.POST['username'],
                            password=request.POST['password'],
                            first_name=request.POST['firstname'],
                            last_name=request.POST['lastname'])

    login(request, new_user)
    return redirect('/hangman/')
