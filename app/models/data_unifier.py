import json
from datetime import datetime
from enum import IntEnum, Enum


class StackOverflowTier(IntEnum):
    A = 25000
    B = 20000
    C = 1000
    D = 200


class RedditTier(IntEnum):
    A = 134000
    B = 34000
    C = 7600
    D = 1400


class CodeProjectTier(IntEnum):
    A = 1197500
    B = 540000
    C = 130000
    D = 19000


class TierScore(float, Enum):
    A = 0.9
    B = 0.7
    C = 0.5
    D = 0.3
    N = 0.1


class UnifiedData:
    def __init__(self, data):
        self.__links = data["link"]
        try:
            self.__tags = data["tags"]
        except KeyError:
            self.__tags = []
        self.__question = data['question']
        self.__answers = data['answers']
        self.__source = data['source']
        self.__saved_time = int(datetime.utcnow().timestamp())
        # Check original source
        if self.__source == 'stackoverflow':
            self.unify_so()
        elif self.__source == 'reddit':
            self.unify_reddit()
        elif self.__source == 'codeproject':
            self.unify_cp()

    # Convert StackData to UnifiedData
    def unify_so(self):
        # Step 1: calculate traffic
        time_interval = datetime.utcfromtimestamp(self.__question['last_activity_date']) \
                        - datetime.utcfromtimestamp(self.__question['creation_date'])
        try:
            traffic_rate = int(self.__question['view_count']/time_interval.days)
        except ZeroDivisionError:
            traffic_rate = int(self.__question['view_count']/1)
        self.__question['traffic_rate'] = traffic_rate

        # Step 2: remove no-need attrs
        self.__question.pop('creation_date')
        self.__question.pop('last_activity_date')
        self.__question.pop('view_count')

        # Step 3: Set owner tier score for each answers
        self.get_reputation_tier(tier_class=StackOverflowTier, attr="owner_reputation")

        # Step 4: Normalize answer scores
        self.score_normalization(attr="score")

    # Convert RedditData to UnifiedData
    def unify_reddit(self):
        # Step 1: Calculate traffic
        time_interval = datetime.utcnow() \
                        - datetime.utcfromtimestamp(self.__question['subreddit']['created_utc'])
        self.__question['traffic_rate'] = self.__question['subreddit']['subscribers'] / time_interval.days

        # Step 2: Remove no-need attrs
        self.__question.pop('subreddit')

        # Step 3: Decide owner reputation tier
        self.get_reputation_tier(tier_class=RedditTier, attr="author_comment_karma")

        # Step 4: Normalize vote
        self.score_normalization(attr="total_vote")

        # Step 5: Rename content name
        for ans in self.__answers:
            ans['content'] = ans['dialogue']
            ans.pop('dialogue')

    # Convert CodeProjectData to UnifiedData
    def unify_cp(self):
        # Step 1: Assign 0 to traffic rate (No related data)
        self.__question["traffic_rate"] = 0

        # Step 2: Decide user reputation tier
        self.get_reputation_tier(tier_class=CodeProjectTier, attr="user_reputation")

        # Step 3: Calculate score rate
        for ans in self.__answers:
            if ans["type"] == "acceptedAnswer":
                ans["score"] += 1
                ans["vote_count"] += 1
            try:
                ans["score"] = ans["score"]/ans["vote_count"]
            except ZeroDivisionError:
                ans["score"] = 0
            ans.pop("vote_count")
            ans.pop("type")

    # Decide Owner Reputation Tier
    def get_reputation_tier(self, tier_class, attr):
        for ans in self.__answers:
            if ans[attr] >= tier_class.A:
                tier = TierScore.A.value
            elif tier_class.A > ans[attr] >= tier_class.B:
                tier = TierScore.B.value
            elif tier_class.B > ans[attr] >= tier_class.C:
                tier = TierScore.C.value
            elif tier_class.C > ans[attr] >= tier_class.D:
                tier = TierScore.D.value
            else:
                tier = TierScore.N.value
            ans['owner_tier'] = tier
            ans.pop(attr)

    # Min-Max normalization for scores
    def score_normalization(self, attr):
        epsilon = 1e-8
        s_list = [ans[attr] for ans in self.__answers]
        if len(s_list) > 0:
            min_value = min(s_list)+epsilon
            max_value = max(s_list)+epsilon
            if min_value == max_value:
                normalized_data = [s / min_value for s in s_list]
            else:
                normalized_data = [(x - min_value) / (max_value - min_value) for x in s_list]
            for idx in range(len(normalized_data)):
                self.__answers[idx]['score'] = normalized_data[idx]
                if attr != "score":
                    self.__answers[idx].pop(attr)

    def get_result(self):
        result = {
            "link": self.__links,
            "tags": self.__tags,
            "question": self.__question,
            "answers": self.__answers,
            "source": self.__source,
            "saved_time": self.__saved_time
        }
        return result


if __name__ == "__main__":
    with open('../test/TestCases_UnitTest_UnifyData/test_cp.json', 'r', encoding="utf-8") as file:
        # test_so = json.load(fp=file)
        # test_reddit = json.load(fp=file)
        test_cp = json.load(fp=file)

    # unifier = UnifiedData(test_so)
    # unifier = UnifiedData(test_reddit[0])
    for cp in test_cp:
        unifier = UnifiedData(cp)
        print(unifier.get_result())



