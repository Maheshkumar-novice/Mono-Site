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
