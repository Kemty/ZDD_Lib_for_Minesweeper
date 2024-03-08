from minesweeper import Minesweeper, TargetBoard
from random import sample

if __name__ == "__main__":
    with open("ZDD_lib\\output\\experiment1_dataset.txt", 'w') as dataset:
        H, W = 20, 20
        for B in [40, 80, 120]:
            for K in [40, 120, 200]:
                for i in range(1, 11):
                    dataset.write(f"B={B}, K={K}, i={i}\n")
                    minesweeper = Minesweeper(H, W, B, False)
                    minesweeper.target_board = TargetBoard(H, W, B)
                    safe_places = [(i, j) for i in range(H) for j in range(W)
                                if not minesweeper.target_board.is_bomb(i, j)]
                    for i, j in sample(safe_places, K):
                        minesweeper.open(i, j)
                    for row in minesweeper.playing_board:
                        dataset.write("".join(row) + "\n")
    print("complete.")