### TODO:
* Add an SQLite Database to store the comments. It could maybe be just one comment table with a parent_id and video_id attribute.
* Mine data from the 2 videos above
* Extract the set of commentators from both videos and check how many commented under both (I am hoping between 200 and 1000)


https://www.fox9.com/news/which-podcasts-have-kamla-harris-donald-trump-done

* Il Sottografo con nodi aventi grado >= 2 è interessante.
* Il sottografo con nodi che hanno interagito in almeno due video è poco interessante: la maggior parte dei nodi è isolata.   
  E' poco interessante anche se applico il subgraph direttamente al primo sottografo.

------------------------

### RQ?:

“How does the structure and tone of engagement around tariff-related discussions differ across partisan platforms 
(Truth vs Bluesky), and what does this reveal about echo chamber formation?”

“How do partisan communities engage with each other on neutral platforms like YouTube, and what 
do those interactions reveal about conversational dynamics between political groups?”

------------------------

### What to do for the Analysis

Before starting the analysis these are the numbers I have:
- On Truth: 30k accounts and 75k posts
- On BlueSky: 15k accounts and 20k posts
- On Youtube: 18 videos (13 for trump, 5 for harris), 60k accounts and 115k comments

Questions: 
- Do I need to extract # of followers and following for each account?
- Should I extract the bio from the accounts? Could be significant to understand the stance / compare the stance
- Are the Social Media Platforms a good choice for this? Are they polarized? Can you measure that?


FOR Truth vs Bluesky:

**- Consider Normalizing Networks by having two Networks with around same number of nodes (same order)
- Visualize the networks
1. Basic measures:
  - Size and Order
  - Density
  - Average Degree <-- CORRELATION BETWEEN IN DEGREE AND OUT DEGREE? JOINT DISTRIBUTION <-- There's basically none (0)
  - Connected Components
2. Centralization and influence:
  - Degree Distribution (Centralization?)
  - Degree Centrality and Betweenness Centrality
3. Activity Inequality: > I USE THEM TO COMPARE THE DISTRIBUTIONS OF COMMENTS IN EACH NETWORK > DONE, VERY INTERESTING
  Compare with Random Network Models -> 2x Configuration Model and 1x Poisson Degree Distribution
    - Gini Coefficient on comments per user
    - Lorenz Curve
4. Echo Chambers Theory (requires Machine Learning for content labeling)
ECHO CHAMBERS -> ECHO CHAMBERS THEORY:
   1. Stance Assortativity (SELECTIVE EXPOSURE)
   2. Stance Homogeneity within Communities (Check out Homophily from Echo Chambers paper)
   3. Information Diffusion Simulation (SIR Model - Check out part 2 from Echo Chambers paper)



FOR Youtube:
- This time I don't need to normalize the network.
- Visualize it
1. Basic Metrics:
   - Size and Order
   - Density
   - Degree Distribution
   - Components
   - Bonus: Some stats about the videos and the asymmetry in volume
2. Community Detection and coloring, just to see what's up
3. DELIBERATIVE DEMOCRACY THEORY (identifying cross-partisan threads and their characteristics):
   1. Stance Labeling of content using LLMs (Left, Neutral, Right) or not LLMs
   2. Aggregate for User-Level stance -> Categorize users
   3. Analyze Comment Threads in general (see paper Etta et al.) <-- CODICE PRONTO
      For each of these metrics, distribution and average -> And compare those with root stance left and root stance right:
      - Tree Size
      - Tree Depth
      - Wiener Index
      - Stance Ratio 
      - Assortativity on Stance
      - Number of Unique users
      - Root Stance
   4. Find Cross-Partisan Interactions (see Wu & Resnick paper) -> Do they match bridges? <-- CODICE PRONTO (Meno la parte dei bridge)
   5. Interaction Outcome Analysis with LLMs for these Cross-Partisan conversations
      - Tone (Hostile, Neutral, Friendly)
      - Escalation (Does the conflict increase?)
      - Agreement or Disagreement?
      - Other things...
      - Any Dominant Tone / Last words
   6. Refection on LLMs Bias and Credibility

    
------------------------

Notes:
- When users from opposing stances reply, do they reinforce, shift, or escalate?
- Are these discussions less likely to continue (shorter threads)?
- Does one side dominate the conversation?

NOW WHAT:
- Figure out content labeling with and without an LLM:
  - PoliticalBiasBERT https://huggingface.co/bucketresearch/politicalBiasBERT
    - Needs to be set for regression (labeling [-1,1])
    - I need around 1000 labeled examples
    - I can then train it and run it on my 75k examples.
  - A GPT Model (don't know which one yet) for second part


------------------------




Youtube Statistics

trump_podcasts = [
    "xrFdHO7FH8w", # LOGAN PAUL <-- 6,919,229 views and 23,451 Comments
    "blqIZGXWUpU", # ALL IN PODCAST <-- 3,546,156 views and 12,693 Comments
    "s11uIW7wi-E", # ADIN ROSS <-- 2,862,938 views and 23,369 Comments
    "vC5cHjcgt5g", # THEO VON <-- 16,885,186 views and 67,194 Comments
    "G80iLTctFuY", # SHAWN RYAN SHOW <-- 4,506,617 views and 26,421 Comments
    "qCbfTN-caFI", # LEX FRIEDMAN <-- 7,654,694 views and 57,831 Comments
    "Ry1IjOft95c", # FLAGRANT <-- 9,608,703 views and 49,343 Comments
    "S7BTdUaNQM8", # FULL SEND PODCAST <-- 3,376,579 views and 5,465 Comments
    "1SsmPh8gCxU", # BUSSIN WITH THE BOYS <-- 479,673 views and 2,982 Comments
    "-dmwG54QsKc", # PBD PODCAST <-- 3,281,899 views and 24,990 Comments
    "nwQil7tcImI", # OUTKICK <-- 1,527,558 views and 10,564 Comments
    "G9lXnwuZ2qs", # SIX FEET UNDER <-- 1,168,871 views and 10,188 Comments
    "hBMoPUAeLnY"  # JRE <-- 58,997,908 views and 535,832 Comments
]

harris_podcasts = [
    "_KCRsjPCiCI", # CALL HER DADDY <-- 990,083 views and 30,356 Comments
    "bzThwqnQJDY", # ALL THE SMOKE <-- 709,935 views and 28,536 Comments
    "7L4sts7I3xI", # BREAKFAST CLUB <-- 588,647 views and 36,869 Comments
    "pNbwMrBMGgE", # THE HOWARD STERN SHOW <-- 1,893,939 views and 9,251 Comments
    "Vu5yD3fu6A8", # CLUB SHAY SHAY <-- 1,711,984 views and 73,014 Comments
]