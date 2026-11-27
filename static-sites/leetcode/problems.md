<!--
The LeetCode page reads this file. Add new problems at the end; the page numbers them in this order.

Each problem:
  # Title
  - Level: Medium | Hard
  - Pattern: the idea it teaches (used for the "By pattern" list; not shown on the problem itself)
  - LeetCode: its number
  - Link: https://leetcode.com/problems/<slug>/

  ## Problem      (always shown; written in our own words, not copied from LeetCode)
  ## Concept
  ## Why it fits
  ## Steps
  ## Try by hand
  ## Answers
  ## Key idea
  ## Code         (always last)

Every section after Problem starts folded. Write a < in text inside `backticks`.
Keep code lines short, about 38 characters fit on a phone: put comments on their own line.
-->

# Longest Consecutive Sequence

- Level: Medium
- Pattern: Hashing
- LeetCode: 128
- Link: https://leetcode.com/problems/longest-consecutive-sequence/

## Problem

You get a list of whole numbers in no particular order. Find the length of the longest run of numbers that follow each other with no gap, like 4, 5, 6, 7.

The numbers can be anywhere in the list, and a repeated number counts once. Your answer has to run in **O(n)** time, so sorting is out.

`[100, 4, 200, 1, 3, 2]` → `4`, because 1, 2, 3 and 4 are all there.

## Concept

**Hashing: a set for instant lookups.** A hash set answers "is this number here?" in O(1) on average, however big the list is.

On top of that, one trick: **only start counting from the first number of a run.**

## Why it fits

- The obvious way is to sort, then walk along counting runs. Sorting is O(n log n), and the problem asks for O(n).
- Look at what you really need to know about a number x: is x + 1 here? Is x + 2 here? Those are yes-or-no lookups, which is exactly what a set is fast at.
- But counting up from *every* number repeats work. If 1 to 10,000 are all there, counting from 1 takes 10,000 steps, from 2 takes 9,999, and so on. That's O(n²).
- The fix: x is the start of a run only when x − 1 is **not** in the set. Count only from those starts, and each number gets counted once, as part of its own run.

## Steps

1. Put every number into a set. Repeats disappear.
2. Go through the numbers **in the set**, not the original list.
3. For each number x, check whether x − 1 is in the set. If it is, skip x: it sits in the middle of a run that gets counted from its start.
4. If x − 1 is missing, x starts a run. Count upward (x + 1, x + 2, …) for as long as the numbers are in the set.
5. Keep the longest count you see. That's the answer.

Why step 2 loops over the set: if the list held the start of a long run many times over, looping over the list would count that whole run again for every copy.

**Time:** O(n). Each number is looked at once by the loop, and at most once more while its run is counted. **Space:** O(n) for the set.

## Try by hand

For each list, write down the set, mark which numbers start a run, and count from each start.

1. `[9, 1, 4, 7, 3, -1, 0, 5, 8, -1, 6]`
2. `[1, 2, 0, 1]`
3. `[10, 30, 20]`
4. `[]`

## Answers

1. **7.** The set is {−1, 0, 1, 3, 4, 5, 6, 7, 8, 9}. −1 is a start (−2 is missing), giving −1, 0, 1: a run of 3. 3 is a start (2 is missing), giving 3 to 9: a run of 7. Every other number has its x − 1 in the set, so it's skipped. The repeated −1 changes nothing.
2. **3.** The set is {0, 1, 2}. Only 0 is a start: 0, 1, 2.
3. **1.** The set is {10, 20, 30}. All three are starts, but none has its x + 1, so each run is 1 long.
4. **0.** The set is empty, so the loop never runs and the answer stays 0.

## Key idea

Only count from the start of a run: a number whose x − 1 is missing.

## Code

```python
class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        seen = set(nums)
        best = 0
        for x in seen:
            # not a start: skip it
            if x - 1 in seen:
                continue
            # a start: count its run
            length = 1
            while x + length in seen:
                length += 1
            best = max(best, length)
        return best
```

# Trapping Rain Water

- Level: Hard
- Pattern: Two pointers
- LeetCode: 42
- Link: https://leetcode.com/problems/trapping-rain-water/

## Problem

You get a list of whole numbers, none below zero. Each number is the height of a wall one unit wide, and the walls stand side by side in a row. Rain falls on the row and fills the dips. Work out how many units of water stay trapped when it stops.

Water spills off either end of the row. Aim for **O(n)** time. The best answer also uses only **O(1)** extra space: a few variables, no extra lists.

`[4, 2, 0, 3, 2, 5]` → `9`, because the dip between the 4 and the 5 holds 2 + 4 + 1 + 2 units.

## Concept

**Two pointers from both ends.** One pointer starts at each end of the list, and they step toward each other until they meet. That covers the whole list in one pass, with no extra lists.

On top of that, one trick: **water at a spot rises to the shorter of the tallest wall on its left and the tallest wall on its right.** So always move the side whose tallest wall is lower, because that side's water level is already settled.

## Why it fits

- The obvious way: for each spot, scan left for its tallest wall and right for its tallest wall. That's O(n²).
- A better way fills two lists first: the tallest wall so far from the left, and from the right. That's O(n) time, but O(n) extra space.
- What you really need at a spot is only the **smaller** of those two walls. If the tallest wall seen from the left is lower than the tallest seen from the right, the left spot's level is the left one. Whatever sits in between can only make its right side taller, not shorter.
- So keep just two numbers, the tallest wall seen from each end, and settle the lower side each step. One pass, O(1) space.
- Trap: update the tallest wall **before** adding water. When the current wall is the new tallest, it adds 0 instead of a negative amount.

## Steps

1. Put the left pointer on the first wall and the right pointer on the last. Set left max, right max and the total to 0.
2. While the left pointer is still before the right one, repeat steps 3 to 5.
3. Update left max with the wall under the left pointer, and right max with the wall under the right pointer.
4. If left max is smaller, the left spot holds left max − its height. Add that to the total and step the left pointer right.
5. Otherwise, the right spot holds right max − its height. Add that and step the right pointer left. A tie lands here too: with equal maxes, the level is the same either way.
6. When the pointers meet, return the total.

Why step 4 is safe: the left spot's tallest wall on the left is exactly left max. Its tallest wall on the right is at least right max, which is already bigger. So the shorter of the two is left max, whatever lies between the pointers.

Why stopping when they meet misses nothing: the pointers always meet on a tallest wall, and the tallest wall holds no water.

**Time:** O(n). Each step moves one pointer by one spot, so there are at most n steps. **Space:** O(1). Just a few numbers, however long the list.

## Try by hand

For each list, write down left max, right max, which side moves, and the water it adds. Count positions from 0.

1. `[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]`
2. `[5, 4, 1, 2]`
3. `[3, 0, 0, 3]`
4. `[7]`

## Answers

1. **6.** Early on, position 2 (height 0) sits under left max 1 and adds 1. Then the right side moves for a while: position 9 (height 1) sits under right max 2 and adds 1. When the right pointer reaches the 3 at position 7, right max becomes 3, so the left side moves for the rest. Positions 4, 5 and 6 sit under left max 2 and add 1, 2 and 1. Total 1 + 1 + 1 + 2 + 1 = 6.
2. **1.** Left max is 5 from the first step, so the right side moves every time. The 2 adds 0. The 1 sits under right max 2 and adds 1. Then the 4 becomes right max and adds 0. The 4 is taller than the 2, but it stands on the 1's left, so the 1 still only fills to 2.
3. **6.** Both maxes are 3 from the first step. Every step is a tie, so the right side moves each time. The 3 on the right adds 0, then each 0 adds 3 − 0 = 3.
4. **0.** Both pointers start on the same spot, so the loop never runs. One wall can't hold water.

## Key idea

Water rises to the lower side's tallest wall, so always settle the lower side first.

## Code

```python
class Solution:
    def trap(self, height: List[int]) -> int:
        h = height
        l, r = 0, len(h) - 1
        lmax = rmax = 0
        water = 0
        while l < r:
            # tallest wall each side
            lmax = max(lmax, h[l])
            rmax = max(rmax, h[r])
            # lower max sets the level
            if lmax < rmax:
                water += lmax - h[l]
                l += 1
            else:
                water += rmax - h[r]
                r -= 1
        return water
```

# Minimum Window Substring

- Level: Hard
- Pattern: Sliding window
- LeetCode: 76
- Link: https://leetcode.com/problems/minimum-window-substring/

## Problem

You get two strings, `s` and `t`. Find the shortest substring of `s` (a stretch of letters that sit next to each other) that holds every letter of `t`. Repeats count: if `t` has two a's, the stretch needs at least two a's. The letters can come in any order, and other letters can sit among them.

Capital and small letters are different, so an `A` doesn't count as an `a`. If no stretch works, return an empty string. The tests make sure there's never a tie for shortest. Both strings can be 100,000 letters long, so aim for **O(m + n)** time, where m is the length of `s` and n the length of `t`. That means the work grows in step with the two lengths: double them, and the work only doubles.

`s = "ADOBECODEBANC"`, `t = "ABC"` → `"BANC"`, because those four letters hold an A, a B and a C, and no shorter stretch does.

## Concept

**Sliding window.** A *window* is a stretch of items that sit next to each other, like letters 2 to 5 of a word. You track it with two *pointers*. A pointer is just a number that remembers a position: here `l` marks the window's left edge and `r` its right edge. "Sliding" means you nudge those edges forward a step at a time, instead of starting fresh for every possible stretch.

Picture a caterpillar crawling along a ruler. Its head reaches forward to take in more, then its tail pulls up behind to let go. Neither ever goes backwards, so the whole crawl is a single trip. For a "shortest stretch" question, the right edge is the head: push it forward until the window is good enough. The left edge is the tail: pull it in while the window stays good, to make it as short as possible.

A tiny case: the shortest run in `[1, 4, 2, 3, 5]` that adds up to at least 7.

- Grow to 1, 4, 2: sum 7, good, length 3. Drop the 1: sum 6, not good.
- Grow to 4, 2, 3: sum 9, good. Drop the 4: sum 5, not good.
- Grow to 2, 3, 5: sum 10, good. Drop the 2: 3 and 5 make 8, still good, length 2. Drop the 3: not good, and nothing is left to take in.
- Shortest: **2**.

Each number joined once and left at most once. That's what makes a sliding window fast: **O(n)** time, where n is the length, meaning double the list and the work only doubles. Checking every possible stretch one by one is at least **O(n²)**: double the list, four times the work. Reach for a sliding window when you want the shortest or longest stretch that meets a rule, and you can update "is it good?" cheaply as one item joins or leaves.

**The extra trick: a tally of what's still needed.** To know when the window holds all of `t`, keep a *counter*: a small table from each letter to a number, like a shopping list with amounts ("a: 2, b: 1"). In Python it's a `Counter`, a kind of *hash map*: a table that jumps straight to any letter's entry, so reading or changing one takes the same tiny time however big the table gets. Fill it from `t`, and keep one more number, `missing`: how many letters you're still short, counting repeats. It starts at the length of `t`.

- A letter joins the window: lower its amount by 1. If it was above 0, you really needed it, so lower `missing` too.
- A letter leaves the window: raise its amount by 1. If it's now above 0, you're short of it again, so raise `missing`.

Say `t = "aab"`. The tally is a: 2, b: 1, and missing is 3. The window takes in `a` (a: 1, missing 2), then `x` (x: −1, a spare, missing stays 2), then `a` (a: 0, missing 1), then another `a` (a: −1, a spare, missing stays 1), then `b` (b: 0, missing 0). Missing is 0, so everything is in.

Why it's true: a letter's amount is always "how many `t` wants, minus how many the window has". Above 0 means short, 0 means just enough, below 0 means spares. Letters `t` doesn't want start at 0 and sink below it while they're in the window, so they never touch `missing`. So `missing` hits 0 exactly when nothing is short, and "is everything in?" is one look at one number.

## Why it fits

- The obvious way: try every substring of `s` and check whether it holds all of `t`. A string of n letters has about n²/2 substrings, so 100,000 letters means around 5 billion of them, before you even check one. Far too slow.
- What you really need: for each spot where a stretch could end, the shortest good stretch ending there. The shortest of those is the answer.
- A sliding window finds exactly that. Push the right edge until the window holds all of `t`, then pull the left edge in for as long as it still does. Each letter of `s` joins once and leaves at most once, so it's one pass.
- The tally plus `missing` makes "is everything in?" instant, so every step costs the same tiny amount.
- Traps: repeats in `t` (if `t` is "aa", one a isn't enough, which is why the tally counts), and capital letters, which are different letters entirely.

## Steps

1. Fill the tally from `t`: each letter and how many times it appears. Set `missing` to the length of `t`, put the left edge `l` at 0, and note that no answer has been found yet.
2. Move the right edge `r` through `s`, one letter at a time. Each new letter joins the window: lower its amount, and if it was above 0, lower `missing`.
3. While `missing` is 0, the window from `l` to `r` holds all of `t`. Repeat steps 4 and 5 until something is missing again.
4. If this window is shorter than the best so far, remember where it starts and how long it is.
5. Let go of the letter at `l`: raise its amount, and if that takes it above 0, raise `missing`. Then move `l` one step right.
6. When `r` has passed the last letter, cut out the best window and return it. If none was found, return an empty string.

Why step 4 comes before step 5: once you let go of a letter, the window may stop being good, and you'd miss recording it.

Why `l` never has to move back: `l` only passes a spot after the window starting there was found good and recorded. Any later window starting at that same spot would end further right, so it would be longer. It can't win.

Why remember a start and a length, not the letters themselves: copying the letters every time a shorter window turns up can add up on long strings. Two numbers are enough, and you cut the piece out once at the end.

**Time:** O(m + n). Filling the tally reads `t` once. Then `r` walks through `s` once, `l` walks through it at most once, and each tally change is instant. **Space:** O(1) extra, meaning a fixed amount however long the strings are. The tally has one entry per different letter, and with only a–z and A–Z there are at most 52.

## Try by hand

For each pair, write down the tally and `missing` as each letter joins or leaves, and every window you record. Count positions from 0.

1. `s = "acbbaca"`, `t = "aba"`
2. `s = "BaAcb"`, `t = "ab"`
3. `s = "banana"`, `t = "abb"`
4. `s = "z"`, `t = "z"`

## Answers

1. **"baca"**. The tally starts a: 2, b: 1, missing 3. Letters 0 to 2 (a, c, b) bring missing to 1, and the second b at 3 is a spare (b: −1). The a at 4 makes missing 0: record "acbba" (start 0, length 5). Letting go of the a at 0 makes a: 1, so missing is 1 again. The c at 5 is a spare, and the a at 6 makes missing 0. Now shrink: "cbbaca" (6 long) and, after dropping the c, "bbaca" (5) don't beat 5. Dropping the b at 2 only takes b from −1 to 0, so the window stays good: "baca", length 4, is the new best. Dropping the b at 3 makes b: 1 and missing 1. The string ends.
2. **"aAcb"**. The tally is a: 1, b: 1, missing 2. The `B` is a spare, because a capital B isn't a b. The `a` makes missing 1. The `A` and the `c` are spares. The `b` makes missing 0: record "BaAcb", length 5. Drop the B, a spare, and the window stays good: "aAcb", length 4, is the new best. Drop the a: missing 1. The string ends.
3. **""**, an empty string. The tally is a: 1, b: 2, missing 3. The b at 0 and the a at 1 bring missing to 1. Every later letter is an a or an n, and they're all spares. Missing never reaches 0, so nothing is recorded. Every letter of `t` is in `s`, but `s` has only one b.
4. **"z"**. The z at 0 makes missing 0: record "z", length 1. Letting go of it makes missing 1 again, and the string ends. A window can be a single letter.

## Key idea

Grow the right edge until nothing is missing, then pull in the left edge until something is.

## Code

```python
class Solution:
    def minWindow(self, s: str, t: str) -> str:
        # the tally: still wanted
        need = Counter(t)
        missing = len(t)
        # no window found yet
        start, size = 0, math.inf
        l = 0
        for r, ch in enumerate(s):
            # ch joins the window
            if need[ch] > 0:
                missing -= 1
            need[ch] -= 1
            # all of t is in: shrink
            while missing == 0:
                if r - l + 1 < size:
                    start = l
                    size = r - l + 1
                # let go of s[l]
                need[s[l]] += 1
                if need[s[l]] > 0:
                    missing += 1
                l += 1
        if size == math.inf:
            return ""
        return s[start:start + size]
```

# Sliding Window Maximum

- Level: Hard
- Pattern: Sliding window
- LeetCode: 239
- Link: https://leetcode.com/problems/sliding-window-maximum/

## Problem

You get a list of whole numbers and a number k. Picture a frame that covers k numbers side by side. It starts over the first k numbers, then moves right one place at a time until it covers the last k. Each time it stops, note the biggest number inside it. Return all of those, in order.

k is always at least 1 and never more than the length of the list. The list can hold 100,000 numbers and k can be nearly as big, so looking through every frame from scratch is far too slow. Aim for **O(n)** time, where n is the list's length: the work grows in step with the list, so twice the numbers means about twice the work.

`[1, 3, -1, -3, 5, 3, 6, 7], k = 3` → `[3, 3, 5, 5, 6, 7]`. The first frame holds 1, 3 and −1, so 3. The next holds 3, −1 and −3, so 3 again. Then −1, −3 and 5 give 5, and so on.

## Concept

**Sliding window.** A window is a stretch of items that sit next to each other in a list, like the frame in this problem. Sliding it means moving it one place to the right: one new item comes in on the right, one old item drops off on the left, and the rest stay. Think of a train window that shows three houses at a time. Each time the train moves on by one house, one house appears, one disappears, and the other two are the same as before. So instead of looking at the whole stretch again, you only deal with what changed.

A tiny case: add up every 3 numbers in a row in `[2, 5, 1, 4, 3]`. The first window, 2, 5, 1, adds to 8. Slide: 4 comes in and 2 drops off, so 8 + 4 − 2 = 10. Slide again: 3 comes in and 5 drops off, so 10 + 3 − 5 = 8. Each slide costs one add and one take-away, however wide the window is. It suits questions about "every stretch of k items in a row", or "the longest stretch that follows some rule".

On top of that, one trick: **keep a line of candidates, biggest at the front, falling towards the back.** A sum is easy to update, because you can take away the number that drops off. The biggest number isn't: when it drops off, you can't know the next biggest without looking through the whole window again. So keep a short line of the numbers that could still become the biggest, ready to take over.

Why can numbers be thrown out of that line? Picture finding the tallest person in a room, where people leave in the same order they came in. If someone taller walks in after you, you'll never be the tallest again: they stay in the room as long as you do, and longer. Numbers in the window work the same way, because they drop off in the order they came in. So when a new number arrives, every number before it that's smaller or equal can go for good.

That gives the rule: when a number arrives, remove numbers from the back of the line while they're not bigger than it, then add it at the back. Say the window is 3 wide and 4, 2, 3 come in. 4 joins. 2 is smaller, so it waits behind: 4, 2. 3 removes the 2 and stops at the bigger 4: 4, 3. The front, 4, is the biggest. Next 1 arrives and the 4 slides out of the window, so 4 leaves the front and 1 joins the back: 3, 1. The front, 3, is the biggest of 2, 3, 1. The line always falls from front to back, so the front is always the biggest. It's also in arrival order, so whatever slides out of the window can only be at the front.

That line needs adding and removing at both ends, which is what a **deque** does (said "deck", short for double-ended queue): a line you can add to or remove from at either end, each in one quick step. Python has one called `deque`. Our line holds each number's **index**, its position in the list counting from 0, rather than the number itself. That way you can tell when the front has slid out of the window.

## Why it fits

- The obvious way: for every window, look through its k numbers for the biggest. There are about n windows and each costs k steps, so that's O(n × k): the work grows with the list's length times the window's width. With 100,000 numbers and k = 50,000, that's billions of steps.
- Sliding alone isn't enough. Taking in the new number is easy, but when the biggest drops off the left, you'd have to look through the whole window again to find the next biggest.
- What you really need is the next biggest already waiting, every time the biggest leaves. The line of candidates is exactly that: the front is the biggest now, the one behind it takes over when the front leaves, and so on.
- It stays fast because each index joins the line once and leaves it at most once. One step might clear out many, but over the whole list that adds up to at most n removals.
- Trap: store indexes, not the numbers. With just the numbers, you can't tell whether the front has slid out of the window.

## Steps

1. Make an empty deque for the candidates' indexes, and an empty answer list.
2. Walk through the list from left to right. Call the current index i and its number x. Do steps 3 to 5 for each one.
3. **Drop the one that left.** The window now covers indexes i − k + 1 to i, so index i − k has just slid off the left. If the front of the deque is i − k, remove it. Only the front can be that old, because the deque keeps indexes in the order they came in. Early on, i − k is below 0, so nothing leaves.
4. **Clear out the losers.** While the number at the back of the deque is smaller than or equal to x, remove it. It came in before x and isn't bigger, so x outlasts it and it can never be the biggest again. Then add i at the back.
5. **Note the biggest.** Once i reaches k − 1, the window is full for the first time, and it stays full from then on. The front of the deque is the biggest number in it, so add that number to the answer.
6. Return the answer list.

Why step 4 removes equal numbers too: two equal numbers give the same answer, and the newer one stays longer, so the older one is never needed.

Why the front is always the biggest: step 4 keeps the numbers in the deque falling from front to back, and step 3 makes sure every index in it is still inside the window.

**Time:** O(n). Each index goes into the deque once and comes out at most once, so all the removals together add up to at most n, however many happen in a single step. **Space:** O(k). The deque only holds indexes inside the window, so never more than k of them (not counting the answer list).

## Try by hand

For each new number, write down what leaves the front, what gets cleared off the back, the deque afterwards (as numbers, remembering their indexes), and the biggest once the window is full. Count indexes from 0.

1. `[1, 3, 1, 2, 0, 5], k = 3`
2. `[9, 7, 5, 3, 1], k = 2`
3. `[4, -2, 4, 4], k = 3`
4. `[2, -4, 3], k = 1`

## Answers

1. **[3, 3, 2, 5].** Index 1: the 3 clears the 1 before it, so the deque is 3. Index 2: the next 1 is smaller, so it waits: 3, 1. The window is full, so note 3. Index 3: the 2 clears the 1: 3, 2, note 3. Index 4: index 1 slides off the left, so the 3 leaves the front. The 0 waits behind: 2, 0, note 2. Index 5: the 5 clears both: 5, note 5.
2. **[9, 7, 5, 3].** The list only falls, so nothing is ever cleared off the back: each number waits behind the last. Instead the front leaves at every step from index 2 on. The deque goes 9, 7 (note 9), then 7, 5 (note 7), then 5, 3 (note 5), then 3, 1 (note 3). The waiting numbers are exactly the next biggest, ready to take over.
3. **[4, 4].** Index 1: −2 is smaller than 4, so it waits: 4, −2. Index 2: the new 4 clears the −2, and the old 4 too, because equal isn't bigger. The deque is just the 4 at index 2, note 4. Index 3: the last 4 clears that one, note 4. Nothing was lost: the old 4 at index 0 would have slid out at index 3 anyway, and a newer 4 is still there.
4. **[2, −4, 3].** With k = 1, each window is a single number, so the answer is the list itself. In the deque, the front leaves at every step from index 1 on, so it never holds more than one index.

## Key idea

Keep only the numbers that could still win: a newer, bigger one knocks out every smaller one before it.

## Code

```python
class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        a = nums
        # indexes, biggest first
        q = deque()
        out = []
        for i, x in enumerate(a):
            # front left the window
            if q and q[0] == i - k:
                q.popleft()
            # clear out the losers
            while q and a[q[-1]] <= x:
                q.pop()
            q.append(i)
            # window full: note front
            if i >= k - 1:
                out.append(a[q[0]])
        return out
```
