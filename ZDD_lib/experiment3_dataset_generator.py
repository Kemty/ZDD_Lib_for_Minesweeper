from minesweeper import Minesweeper
from random import randrange

if __name__ == "__main__":
    with open("ZDD_lib\\output\\experiment3_dataset.txt", 'w') as dataset:
        for R in [1, 2]:
            for N in [20, 40, 60]:
                B = N * N * R // 10
                print(f"{N}×{N}, B={B}")
                for i in range(1):
                    dataset.write(f"{N}×{N}, B={B}, i={i}\n")
                    minesweeper = Minesweeper(N, N, B, False)
                    si, sj = randrange(minesweeper.H), randrange(minesweeper.W)
                    minesweeper.set_target_board(si, sj)
                    for i in range(N):
                        row = []
                        for j in range(N):
                            if (i, j) == (si, sj):
                                row.append('s')
                            elif minesweeper.target_board.is_bomb(i, j):
                                row.append('#')
                            else:
                                row.append('.')
                        dataset.write("".join(row) + "\n")
            
