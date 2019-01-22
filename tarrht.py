def solution(words):
    def champ_words(start_or_end):

        1s,2s,1e,2e = 0,0,0,0
        for i in range(len(start_or_end)):
            if start_or_end[i][0] > 1s:
                1
                s = start_or_end[i][0]
            elif start_or_end[i][0] > 2s:
                2
                s = start_or_end[i][0]

    total_max = 0
    for letter in "abcdefghijklmnopqrstuwvxyz":
        letter_prefix = 0
        letter_sufix = 0
        letter_whole_word = 0
        champ = []
        whole_flag = False
        for word in words:
            temp_pre = 0
            temp_end = 0

            if word[0] == letter:

                for word_l in word:
                    if word_l == letter:
                        temp_pre += 1
                    else:
                        break
                if temp_pre == len(word):
                    letter_whole_word += len(word)
                    whole_flag = True
                else:
                    whole_flag = False
            if word[-1] == letter and not whole_flag:

                for i in range(1, len(word)):
                    if word[-i] == letter:
                        temp_end += 1
                    else:
                        break

            if not whole_flag:
                if temp_pre > letter_prefix and temp_end < letter_sufix:
                    champ.append([temp_pre, temp_end])
                elif temp_pre > letter_prefix and temp_end <= letter_sufix:
                    letter_prefix = temp_pre
                elif temp_pre <= letter_prefix and temp_end > letter_sufix:
                    letter_sufix = temp_end

        total_max = max(letter_prefix + letter_whole_word + letter_sufix, total_max)
    return total_max