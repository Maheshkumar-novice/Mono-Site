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
