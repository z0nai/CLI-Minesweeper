from colorama import Fore, Back, init
from random import randint
from os import system
from copy import deepcopy
from collections import defaultdict
from time import time

init(autoreset=True)

clear = lambda: system('cls')
COLORS = {
    '1': Fore.CYAN + ' 1',
    '2': Fore.GREEN + ' 2',
    '3': Fore.YELLOW + ' 3',
    '4': Fore.MAGENTA + ' 4',
    '5': Fore.LIGHTYELLOW_EX + ' 5',
    '6': Fore.LIGHTCYAN_EX + ' 6',
    '7': Fore.LIGHTRED_EX + ' 7',
    '8': Fore.BLUE + ' 8',
    '0': Back.WHITE + '  ',
    'x': Fore.RED + ' x',
    'f': Fore.RED + ' f'
}

board_width = int(input('Enter board width: '))
board_height = int(input('Enter board height: '))
board_mines = int(input('Enter mines: '))

cmd = list(map(int, input("Enter your first step:\n").split()))
start_time = time()
pos_of_mines = set()
pos_of_flags = set()


def generate_board(*, width: int, height: int, mines: int, click: list) -> list:
    global pos_of_mines
    check = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    board = [[0 for _ in range(width + 2)] for _ in range(height + 2)]
    mine_check = [(click[1] + dy, click[0] + dx) for dy, dx in check]
    while len(pos_of_mines) != mines:
        mine_y = randint(1, height)
        mine_x = randint(1, width)
        if not (mine_y, mine_x) in mine_check:
            pos_of_mines.add((mine_y, mine_x))
    check.remove((0, 0))
    for mine_y, mine_x in pos_of_mines:
        board[mine_y][mine_x] = 'x'
        for y_check, x_check in check:
            if board[mine_y + y_check][mine_x + x_check] != 'x':
                board[mine_y + y_check][mine_x + x_check] += 1
    return board


def color_board(*, board: list) -> list:
    global COLORS
    board = deepcopy(board)
    for i in range(len(board)):
        board[i] = list(map(str, board[i]))
        for j in range(len(board[i])):
            board[i][j] = COLORS[board[i][j]]
    return board


def generate_groups(*, board: list) -> list:
    height = len(board) - 2
    width = len(board[0]) - 2

    groups_dfs = [[set() for _ in range(width + 2)] for _ in range(height + 2)]
    visited = [[False for _ in range(width + 2)] for _ in range(height + 2)]

    group_id = 0

    def dfs(dfs_y, dfs_x, gid):
        nonlocal groups_dfs, visited
        if visited[dfs_y][dfs_x]:
            return
        visited[dfs_y][dfs_x] = True

        groups_dfs[dfs_y][dfs_x].add(gid)
        top_bottom = {0}
        left_right = {0}
        if dfs_y < height: top_bottom.add(1)
        if dfs_y > 1: top_bottom.add(-1)
        if dfs_x < width: left_right.add(1)
        if dfs_x > 1: left_right.add(-1)
        check = {(check_y, check_x) for check_y in top_bottom for check_x in left_right}
        for dy, dx in check:
            ny, nx = dfs_y + dy, dfs_x + dx
            if board[ny][nx] == 0:
                dfs(ny, nx, gid)
            elif board[ny][nx] != 'x':
                groups_dfs[ny][nx].add(gid)

    for groups_y in range(1, height + 1):
        for groups_x in range(1, width + 1):
            if board[groups_y][groups_x] == 0 and not visited[groups_y][groups_x]:
                dfs(groups_y, groups_x, group_id)
                group_id += 1
    return groups_dfs


def print_board(*, board: list) -> None:
    global board_width, board_height, is_shown, mines_left, start_time
    clear()
    print('  ', *range(1, 10), sep='   ', end='  ')
    print(*range(10, board_width + 1), sep='  ')
    for show_y in range(1, board_height + 1):
        print((' ' if show_y < 10 else '') + str(show_y), end='  ')
        for show_x in range(1, board_width + 1):
            if is_shown[show_y][show_x]:
                print(board[show_y][show_x], end='  ')
            else:
                print(Back.LIGHTBLACK_EX + '  ', end='  ')
        print()
    print(f'mines: {mines_left}')
    print(f'time:  {(time() - start_time):.0f}')


def show(*, operator: str, y: int, x: int, recursive=True) -> str:
    global current_pool, pool, groups, groups_idx, is_shown, mines_left, board_width, board_height
    if operator == 'o':
        if pool[y][x] == 'x':
            if current_pool[y][x] == 'f':
                return 'Game'
            return 'lost'

        if pool[y][x] == 0:
            for show_y, show_x in groups_idx[list(groups[y][x])[0]]:
                is_shown[show_y][show_x] = True
            return 'Game'

        if is_shown[y][x] and recursive:
            top_bottom = {0}
            left_right = {0}
            if y < board_height: top_bottom.add(1)
            if y > 1: top_bottom.add(-1)
            if x < board_width: left_right.add(1)
            if x > 1: left_right.add(-1)
            check = {(y, x) for y in top_bottom for x in left_right}
            check.remove((0, 0))
            for dy, dx in check:
                ny, nx = y + dy, x + dx
                show(operator='o', y=ny, x=nx, recursive=False)
            return 'Game'
        is_shown[y][x] = True


    elif operator == 'f':
        if current_pool[y][x] != 'f' and not is_shown[y][x]:
            current_pool[y][x] = 'f'
            mines_left -= 1
            is_shown[y][x] = True
            pos_of_flags.add((y, x))

        elif current_pool[y][x] == 'f':
            current_pool[y][x] = pool[y][x]
            is_shown[y][x] = False
            mines_left += 1
            pos_of_flags.remove((y, x))

    return 'Game'


pool = generate_board(width=board_width, height=board_height, mines=board_mines, click=cmd)
groups = generate_groups(board=pool)
is_shown = [[False for _ in range(board_width + 2)] for _ in range(board_height + 2)]
current_pool = deepcopy(pool)
mines_left = board_mines
status = 'Game'

groups_idx = defaultdict(set)
for y in range(board_height + 2):
    for x in range(board_width + 2):
        if groups[y][x]:
            for ids in groups[y][x]:
                groups_idx[ids].add((y, x))
for y, x in groups_idx[list(groups[cmd[1]][cmd[0]])[0]]:
    is_shown[y][x] = True

while status == 'Game':
    print_pool = color_board(board=current_pool)
    print_board(board=print_pool)

    cmd = input().split()
    if len(cmd) == 3:
        op, x, y = cmd[0], int(cmd[1]), int(cmd[2])
    while len(cmd) != 3 or not 0 < x < board_width or not 0 < y < board_height:
        cmd = input('Введите верную команду\no/f X Y\n').split()
        if len(cmd) == 3:
            op, x, y = cmd[0], int(cmd[1]), int(cmd[2])

    status = show(operator=op, y=y, x=x, recursive=True)

    if pos_of_flags == pos_of_mines:
        status = 'won'
clear()
print_pool = color_board(board=current_pool)
print_board(board=print_pool)
print()
print('You', status)
print(f'Your time: {(time() - start_time):.0f}')
input()
# add OOP and arrrows support
