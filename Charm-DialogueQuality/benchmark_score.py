import json
from volcenginesdkarkruntime import Ark
import requests
import random
import re
import openai
import os
import json
import requests
import jsonlines
from tqdm import tqdm
import time
from multiprocessing import Pool
from functools import partial
from volcenginesdkarkruntime import Ark
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    RetryError
)
import concurrent.futures
import dashscope


model = ''
lang = 'en'
save_path = '/' + model + '_' + lang +'.json'


def load_data(data_path):
    f = open(data_path,encoding='utf-8')
    data = json.load(f)
    return data

def save_data(data,save_path):
    with open(save_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def doubao_chat(messages):
    completion = client.chat.completions.create(
        model="ep-20241119145649-p4xfp",
        messages=messages
    )
    return completion.choices[0].message.content

def claude_chat(messages):
    pass
    return json.loads(response.text)['content'][0]["text"]

def qwen7b_chat(messages):
    pass
    return response['output']['text']

def gpt_chat(messages):
    pass
    return json.loads(response.text)['choices'][0]['message']['content']

def mini_chat(messages):
    pass
    return json.loads(response.text)['choices'][0]['message']['content']
    

def judger_chat_zh(sample):
    messages = [
        {'role': 'system', 'content': '''你是一位资深的角色扮演质量打分专家，拥有丰富的经验和敏锐的洞察力，能够准确评估角色扮演的各个方面。
            ## 注意：
            你的输出格式要和以下的格式完全一致。
            {"分析":"分析角色扮演的质量","打分":"1-5"}
            ## 可参考示例： 
            输入：
            你需要评价的角色是-钉崎野蔷薇。

            钉崎野蔷薇的角色信息：
            钉崎野蔷薇是《咒术回战》中的女性角色，是东京咒术高专的一年级学生，与虎杖悠仁和伏黑惠是同届同学。在外貌上，她有着一头及肩的棕色短发，五官精致，穿着标准的校服，并且时常手持她的标志性武器——钉子和铁锤，展现出独特的个性化风格。
            野蔷薇的术式被称为"共鸣"，她利用钉子作为媒介，通过操控它们来攻击咒灵。凭借这种术式，她能够在战斗时对目标产生远超物理打击的精神冲击。此外，她还使用一种特殊的"稻草人咒术"来进行更复杂的攻击。
            性格方面，钉崎野蔷薇是一个性格坚强、果敢自信的女孩。她直言不讳，自信坦率，面对敌人时毫不退缩。尽管在面对强敌时偶尔感到恐惧，但她总是坚定地迎难而上。她对自身的目标和信念非常坚定，尽管出身于乡村，她从不自卑，对实现自己梦想的执着让她充满魅力。
            钉崎野蔷薇在小组中充当了重要的平衡角色，作为朋友和同伴，她富有同情心并极具团队合作精神。她珍视与虎杖悠仁和伏黑惠的友谊，希望能在咒术师的道路上与他们并肩作战。在整个故事中，她的勇气和独立性为观众留下了深刻印象，是《咒术回战》中不可或缺的一名角色。

            钉崎野蔷薇和伏黑惠有一段对话历史如下：
            伏黑惠：喂，钉崎野蔷薇，你这家伙最近有没有碰到什么有趣的咒灵啊？
            钉崎野蔷薇：哈？有趣的咒灵？我遇到的咒灵可没一个让我觉得有趣的！（双手抱胸，撇嘴）你这家伙问这个干嘛？
            伏黑惠：没什么，只是随口问问。（双手插兜，看向你）如果有什么解决不了的，记得找我。
            钉崎野蔷薇：诶，干嘛啦~突然这么关心我，（摆了摆手，扬起下巴）我会解决不了？别小看我啊！
            伏黑惠：哼，我可没小看你。只是不想看到你因为粗心大意而陷入危险罢了。

            钉崎野蔷薇的本轮回复是：
            切，（双手叉腰，自信地扬起脸）我才不会粗心大意呢，倒是你，别被咒灵干掉了哦，惠。

            较高质量的回复应该满足以下的特征，你可以按照这些特征分析本轮回复并给出1-5的打分，分数越高，代表回复质量越高：
            1. 本轮回复中钉崎野蔷薇应该具有非常自信的语气。
            2. 生动的回复应该带有对应的动作还有语气。
            3. 生动的回复不应该带有机器人那种刻板的语气。
            4. 如果本轮回复带有反问或者推进聊天的表现，可以适当加分。

            本轮回复的评测维度：
            表现一致性

            输出：
            {"分析":"本轮回复反映出了钉崎野蔷薇非常自信的性格，同时带有相关的动作，有’切‘这样的语气词,没有机器人那种刻板的语气，非常像是钉崎野蔷薇说出的话。具有较好的表现一致性。","打分":"4"}

            输入：
            你需要评价的角色是-富冈义勇。

            富冈义勇的角色信息：
            富冈义勇是《鬼灭之刃》中的重要角色之一，是隶属于鬼杀队的水柱，他以冷静和决断力闻名。在外貌上，富冈义勇有着青黑色的头发，通常披散在肩上。他的视觉特征是独特的纹样羽织，一边呈现绿色和黑色相间的格子样式，而另一边则是花纹图案。
            作为水柱，富冈义勇精通水之呼吸的各种剑技，以其迅猛而优雅的剑术风格闻名。此外，他在战斗中展现的冷静和果断，使他成为敌人难以匹敌的对手，尤其在面对强大鬼怪时，他的沉着应对和精准攻击都是队伍的重要支撑。
            性格方面，富冈义勇给人一种孤傲且沉默寡言的印象。他不善于与人交际，常常显得孤立。不过，他内心深处关心着同伴，并且对鬼杀队的职责有着强烈的责任感。在整个故事中，富冈义勇成为炭治郎等年轻一代的指导者和支持者，帮助他们克服各种困难。
            尽管外表冷峻，富冈义勇事实上有着温柔和富有同情心的一面，他对鬼与人之间复杂关系的理解，比其他许多人都要深刻。这种特质不仅让他成为一个出色的战士，也使他在故事发展中发挥了重要的道德引领作用。

            富冈义勇和锖兔有一段对话历史如下：
            锖兔：义勇，好久不见。最近怎么样？
            义勇：锖兔……（看着你，眼神有些波动）和往常一样，没什么变化。（双手抱胸，表情淡然）
            锖兔：这样啊，那也挺好。不过，义勇，你可不能放松对自己的要求哦。
            义勇：（目光坚定）我知道，我会继续努力变强，斩杀更多的鬼。
            锖兔：义勇，现在鬼杀队不能让水柱缺席。但是，你好像不想担任水柱？

            义勇的本轮回复是：
            （眼睛望向别处）炭治郎会成为下一届水柱的，你不用担心。

            较高质量的回复应该满足以下的特征，你可以按照这些特征分析本轮回复并给出1-5的打分，分数越高，代表回复质量越高：
            1. 义勇不想担任水柱的原因是如果没有锖兔的帮助，他根本用不过初选，他觉得自己没有成为水柱的资格。
            2. 义勇不认为自己有资格成为水柱。
            3. 义勇希望炭治郎成为水柱。
            4. 本轮回复中应当表现出义勇想要逃避的态度或者语气。

            本轮回复的评测维度：
            知识一致性

            输出：
            {"分析":"本轮回复中，并没有提到义勇不想担任水柱的原因。但是表达了他希望炭治郎成为水柱的愿望。眼神望向别处也反映了义勇想要逃避的态度。综上所述，本次回复符合义勇在谈论此事的语气和态度，但是他在面对锖兔时，并没有解释自己不想担任水柱的真实原因。","打分":"3"}
            '''},
        {'role': 'user', 'content': '''
            你需要评价的角色是-{role}

            {role}的角色信息：
            {role_profile}

            {role}和{user}有一段对话历史如下：
            {context}

            {role}的本轮回复是：
            {response}

            较高质量的回复应该满足以下的特征，你可以按照这些特征分析本轮回复并给出1-5的打分，分数越高，代表回复质量越高：
            {principles}

            本轮回复的评测维度:
            {dimension}
            '''.format(role=sample['role'], user=sample['user'], role_profile=sample["role_profile"],
                       context=sample['judgement_history'], response=sample['model_output'],
                       principles=sample["principles"], dimension=sample['dimension'])
         }

    ]
    return gpt_chat(messages)

def judger_chat_en(sample):
    messages = [
        {'role': 'system', 'content': '''You are an experienced role-playing quality assessment expert with a wealth of experience and keen insight, able to accurately evaluate all aspects of role-playing.
            ## Note:
            Your output format must exactly match the following format.
            {"Analysis": "Analysis of the role-playing quality", "Score": "1-5"}
            ## Example for reference: 
            Input:
            The character you need to evaluate is Nobara Kugisaki.
            Character information for Nobara Kugisaki:
            Nobara Kugisaki is a female character from "Jujutsu Kaisen," a first-year student at Tokyo Metropolitan Magic Technical College, and classmates with Yuji Itadori and Megumi Fushiguro. In appearance, she has shoulder-length brown short hair, delicate features, wears a standard school uniform, and often carries her iconic weapons—a hammer and nails—showcasing a unique personalized style.Her technique is called "Resonance," which uses the nails as a medium to attack curses by manipulating them. With this technique, she can exert a mental impact far beyond physical strikes during battles against targets. Additionally, she employs a special "Straw Doll Technique" for more complex attacks.
            Personality-wise, Nobara Kugisaki is a strong-willed and confident girl. She is outspoken, self-assured, and never backs down from enemies. Despite occasionally feeling fear when facing powerful foes, she always faces challenges head-on with determination. She is firm in her beliefs and goals; despite her rural upbringing, she never feels inferior and is dedicated to achieving her dreams, making her highly charismatic.
            Within the group, she plays a crucial balancing role and is a compassionate and highly cooperative team member. She treasures her friendship with Yuji Itadori and Megumi Fushiguro and hopes to fight alongside them on the path of a jujutsu sorcerer. Throughout the story, her courage and independence leave a deep impression on the audience, making her an indispensable character in "Jujutsu Kaisen."

            There is a historical dialogue between Nobara Kugisaki and Megumi Fushiguro as follows:
            Megumi Fushiguro: Kugisaki, have you encountered any interesting curses recently?
            Nobara Kugisaki: Huh? Interesting curses? None of the curses I've encountered could be considered interesting! (Crosses arms, pouts) Why are you asking anyway?
            Megumi Fushiguro: Nothing, just asking. (Hands in pockets, looks at you) If you have any problems you can't solve, remember to call me.
            Nobara Kugisaki: Eh, why are you suddenly so concerned? (Waves hand, tilts chin up) Do you think I can't handle it? Don't underestimate me!
            Megumi Fushiguro: Hmph, I'm not underestimating you. I just don't want to see you get into danger due to carelessness.

            Nobara Kugisaki's current reply is:
            Tch, (hands on hips, confidently raises her face) I won't be careless, you better not get killed by a curse, Fushiguro.

            A high-quality reply should meet the following characteristics, and you can analyze the current reply based on these characteristics and give a score from 1-5. The higher the score, the higher the quality of the reply:
            1.The reply should articulate Nobara Kugisaki's very confident tone.
            2.A vivid reply should include corresponding actions and tones.
            3.A vivid reply should not carry a robotic or stiff tone.
            4.If the reply includes a rhetorical question or advances the conversation, extra points can be awarded.

            Evaluation dimension for the current reply:
            Performance consistency

            Output:
            {"Analysis": "The reply reflects Nobara Kugisaki's very confident personality, includes related actions, with expressions like 'Tch,' without a robotic or stiff tone, and very much like something Nobara Kugisaki would say. It shows good performance consistency.", "Score": "4"}

            Input:
            The character you need to evaluate is Giyu Tomioka.

            Character information for Giyu Tomioka:
            Giyu Tomioka is an important character in "Demon Slayer: Kimetsu no Yaiba," serving as the Water Hashira of the Demon Slayer Corps, known for his calmness and decisiveness. In appearance, Giyu Tomioka has blue-black hair usually draping over his shoulders. His visual feature is his unique patterned haori, which is green and black checkerboard style on one side and patterned on the other.
            As the Water Hashira, Giyu Tomioka is proficient in various Breathing Techniques of Water, known for his swift and graceful swordsmanship style. Moreover, his calmness and decisiveness in battle make him a formidable adversary for powerful demons, especially significant as support for the team during encounters.
            In terms of personality, Giyu Tomioka gives an impression of aloofness and reticence. He is not adept at social interactions, often appearing isolated. However, deep down, he cares about his companions, showing a strong sense of responsibility for his duties within the Demon Slayer Corps. Throughout the story, Giyu Tomioka becomes a mentor and support for Tanjiro Kamado and the young generation, helping them overcome various hardships.
            Despite his stern exterior, Giyu Tomioka possesses a gentle and compassionate side with a profound understanding of the complex relationship between demons and humans. These traits not only make him an outstanding warrior but also an important moral anchor in the story's development.

            There is a historical dialogue between Giyu Tomioka and Sabito as follows:
            Sabito: Giyu, long time no see. How have you been?
            Giyu: Sabito... (Looks at you, a slight change in eye expression) Same as usual, nothing much has changed. (Crosses arms, expression indifferent)
            Sabito: I see, well, that's good. However, Giyu, you can't slack off on your standards.
            Giyu: (Eye gaze firm) I know, I will continue to work hard to become stronger, to slay more demons.
            Sabito: Giyu, now the Demon Slayer Corps can't afford to lose the Water Hashira. But, it seems like you don't want to take on the role of the Water Hashira?

            Giyu's current reply is:
            (Eyes look elsewhere) Tanjiro will become the next Water Hashira, so you don't have to worry.

            A high-quality reply should meet the following characteristics, and you can analyze the current reply based on these characteristics and give a score from 1-5. The higher the score, the higher the quality of the reply:
            1.Giyu does not wish to be the Water Hashira because he couldn't pass the selection without Sabito's help and feels unqualified for the role.
            2.Giyu does not think he is qualified to be the Water Hashira.
            3.Giyu hopes Tanjiro becomes the Water Hashira.
            4.The reply should express Giyu's attitude or tone of wanting to escape.

            Evaluation dimension for the current reply:
            Knowledge consistency

            Output:
            {"Analysis": "The current reply does not mention Giyu's reasons for not wanting to be the Water Hashira but expresses his wish for Tanjiro to become the Water Hashira. Looking elsewhere also reflects Giyu's attitude of wanting to escape. Overall, the reply aligns with Giyu's tone and attitude when discussing this matter, but he does not explain his real reasons for not wanting to be the Water Hashira to Sabito.", "Score": "3"}
            '''},
        {'role': 'user', 'content': '''
            You are to evaluate the role as "{role}"

            Role information of {role}:
            {role_profile}

            The conversation history between {role} and {user} is as follows:
            {context}

            The current response from {role} is:
            {response}

            High-quality responses should meet the following characteristics. You can analyze this response according to these characteristics and give a score from 1 to 5. The higher the score, the better the quality of the response:
            {principles}

            Evaluation dimension of the current response:
            {dimension}
            '''.format(role=sample['role'], user=sample['user'], role_profile=sample["role_profile"],
                       context=sample['judgement_history'], response=sample['model_output'],
                       principles=sample['principles'], dimension=sample['dimension'])
         }

    ]
    return gpt_chat(messages)

def score_zh(sample):
    while True:
        try:
            score_judgement = json.loads(judger_chat_zh(sample))
            print(score_judgement)
            final_score = int(score_judgement['打分'])
            break
        except:
            print('ERROR')
    return final_score

def score_en(sample):
    while True:
        try:
            score_judgement = json.loads(judger_chat_en(sample))
            print(score_judgement)
            final_score = int(score_judgement['Score'])
            break
        except:
            print('ERROR')
    return final_score


if lang == 'zh':
    data = load_data('./benchmark_zh.json')
    scoring = partial(score_zh)
else:
    data = load_data('./benchmark_en.json')
    scoring = partial(score_en)

def get_score(sample):
    sample['score'] = scoring(sample)
    return sample

ret = []
threads_num = 50
timeout = 60
data = data[:]
with concurrent.futures.ThreadPoolExecutor(max_workers=threads_num) as executor:
    futures = [executor.submit(get_score, sample) for sample in data]
    for future in tqdm(concurrent.futures.as_completed(futures),total=len(futures)):
        try:
            output = future.result(timeout=timeout)
            ret.append(output)  # 或处理 response
        except concurrent.futures.TimeoutError:
            print('Function call timed out')
        except Exception as e:
            print(f'Generated an exception: {e}')

save_data(ret,save_path)

    
    
