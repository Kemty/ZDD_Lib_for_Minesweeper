from random import sample

class TargetBoard:
    def __init__(self, H, W, B, si=None, sj=None, board=None):
        """
            si, sj: 初手のヒント数字が0とする場合の, 初手の座標
        """
        self.H = H
        self.W = W
        self.B = B
        if si is None and board is None:
            self.board = self._generate_random_board()
        elif board is None:
            self.board = self._generate_random_board_start_with_zero(si, sj)
        else:
            self.board = board
    
    def _generate_random_board(self):
        board = [[False]*self.W for _ in range(self.H)]
        places_witch_can_put_bomb = list(range(self.H * self.W))
        for e in sample(places_witch_can_put_bomb, self.B):
            i, j = self._to_2d(e)
            board[i][j] = True
        return board
    
    def _generate_random_board_start_with_zero(self, si, sj):
        board = [[False]*self.W for _ in range(self.H)]
        places_witch_cannot_put_bomb = set([(si, sj)]) | set(self._iterate_8d(si, sj))
        places_witch_can_put_bomb = [(i, j) for i in range(self.H) for j in range(self.W)
                                     if (i, j) not in places_witch_cannot_put_bomb]
        for i, j in sample(places_witch_can_put_bomb, self.B):
            board[i][j] = True
        return board
    
    def _to_1d(self, i, j):
        e = i * self.W + j
        return e
    
    def _to_2d(self, e):
        i, j = divmod(e, self.W)
        return i, j
    
    def _iterate_8d(self, i, j):
        D = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
        for di, dj in D:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.H and 0 <= nj < self.W:
                yield ni, nj

    def is_bomb(self, i, j) -> bool:
        return self.board[i][j]
    
    def count_neighbor_bombs(self, i, j) -> int:
        b = 0
        for ni, nj in self._iterate_8d(i, j):
            b += self.board[ni][nj]
        return b

class Minesweeper:
    def __init__(self, H, W, B, do_start_with_zero=True):
        self.H = H
        self.W = W
        self.B = B
        self.do_start_with_zero = do_start_with_zero
        self.playing_board = [['.']*self.W for _ in range(H)]
        self.target_board = None
        self.open_cnt = 0
        self.flag_cnt = 0
    
    def set_target_board(self, si=None, sj=None, board=None):
        self.target_board = TargetBoard(self.H, self.W, self.B, si, sj, board)
    
    def open(self, i, j) -> int|None:
        """
            開放済み or 旗: None
            爆弾マス: -1
            安全マス: ヒント数字 (0 ~ 8)
        """
        if self.playing_board[i][j] != '.':
            return None
        elif self.target_board.is_bomb(i, j):
            return -1
        else:
            h = self.target_board.count_neighbor_bombs(i, j)
            self.playing_board[i][j] = str(h)
            self.open_cnt += 1
            return h
    
    def flag(self, i, j) -> None:
        """
            旗を 追加/削除
            爆弾総数も併せて変動
        """
        if self.playing_board[i][j] == '.':
            self.playing_board[i][j] = 'f'
            self.B -= 1
            self.flag_cnt += 1
        elif self.playing_board[i][j] == 'f':
            self.playing_board[i][j] = '.'
            self.B += 1
            self.flag_cnt -= 1
        
    
    def have_finished(self) -> bool:
        """
            全ての安全マスを開いたか？
        """
        return self.open_cnt == self.H * self.W - (self.B + self.flag_cnt)
    
    def _to_1d(self, i, j):
        e = i * self.W + j
        return e
    
    def _to_2d(self, e):
        i, j = divmod(e, self.W)
        return i, j
    
    def _iterate_8d(self, i, j):
        D = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
        for di, dj in D:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.H and 0 <= nj < self.W:
                yield ni, nj