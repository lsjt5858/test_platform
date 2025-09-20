#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date:  2025/9/19
# @Description: [对文件功能等的简要描述（可自行添加）]
"""mock data utility"""

import random
import string
import time
import uuid

from faker import Faker

from core.base_util.log_util import LogUtil

fake = Faker(locale='zh_CN')


class MockDataUtil:
    """mock data utility"""

    @staticmethod
    def random_gen_name(user_name=None):
        """随机生成一个名称: Auto-{user_name}xxx

        Args:
            user_name(str): 基于user_name生成名称

        Returns:
            str: random name generated
        """
        ticks = str(int(time.time()))
        name = f'auto_{user_name}{ticks}'
        LogUtil.info(f'随机生成的名称： {name}')
        return name

    @staticmethod
    def random_gen_cn_name():
        """随机生成一个中文名"""
        return fake.name()

    @staticmethod
    def random_gen_sex():
        """随机性别"""
        random_gender = fake.random_element(elements=("man", "woman"))
        return random_gender

    @staticmethod
    def random_gen_localized_name(locale: str) -> str:
        """随机生成一个特定地区的人名

        * Reference: https://faker.readthedocs.io/en/master/locales.html

        Args:
            locale(str): e.g.: en_US/en_GB/zh_CN, more options see reference

        Returns:
            str: random localized name
        """
        localized_faker = Faker(locale)
        return localized_faker.name()

    @staticmethod
    def random_gen_localized_address(locale: str) -> str:
        """随机生成一个特定地区的地址

        * Reference: https://faker.readthedocs.io/en/master/locales.html

        Args:
            locale(str): e.g.: en_US/en_GB/zh_CN, more options see reference

        Returns:
            str: random localized address
        """
        localized_faker = Faker(locale)
        return localized_faker.address()

    @staticmethod
    def random_gen_localized_postcode(locale: str) -> str:
        """随机生成一个特定地区的邮编

        * Reference: https://faker.readthedocs.io/en/master/locales.html

        Args:
            locale(str): e.g.: en_US/en_GB/zh_CN, more options see reference

        Returns:
            str: random localized postcode
        """
        localized_faker = Faker(locale)
        return localized_faker.postcode()

    @staticmethod
    def random_gen_localized_phone_number(locale: str) -> str:
        """随机生成一个特定地区的电话号码

        * Reference: https://faker.readthedocs.io/en/master/locales.html

        Args:
            locale(str): e.g.: en_US/en_GB/zh_CN, more options see reference

        Returns:
            str: random localized phone number
        """
        localized_faker = Faker(locale)
        return localized_faker.phone_number()

    @staticmethod
    def random_gen_email():
        """随机生成一个可用的邮箱

        Returns:
            str: random email generated
        """
        rand = str(random.randint(1, 9999999))
        mail = f'auto.mail.{rand}@bytedance.com'

        LogUtil.info(f'使用随机生成的email: {mail}.')
        return mail

    @staticmethod
    def random_gen_mobile_number():
        """随机生成一个手机号码

        Returns:
            str: random mobile number generated
        """
        rand = str(random.randint(1000000, 9999999))
        return f'1340{rand}'

    @staticmethod
    def random_gen_pure_number_serials(num):
        """随机生成一个长度为n的数字字符串，取值范围100...0 - 999...9

        Returns:
            str: random number serials generated
        """
        result = ''
        if num > 0:
            minimum = 10 ** (num - 1)
            maximum = 10 ** num - 1
            result = str(random.randint(minimum, maximum))
        return result

    @staticmethod
    def random_true_or_false():
        return random.random() > 0.5

    @staticmethod
    def true_or_false(probability=50):
        """randomly returns True/False with the given probability

        Args:
            probability(int): 1 - 100, default 50

        Returns:
            bool:
        """
        if probability > 100 or probability < 0:
            raise ValueError("发生概率不可以超过100或小于0")

        seed = random.randint(1, 100)

        return seed <= probability

    @staticmethod
    def random_gen_bankcard_number_serials(num=19):
        """随机生成一个银行卡号，默认是19位

        Returns:
            str: random bankcard generated
        """
        seeds = '1234567890'
        random_num = []
        for _ in range(num):
            random_num.append(random.choice(seeds))
        return "".join(random_num)

    @staticmethod
    def random_gen_string(size=30):
        """随机生成一个字符串 默认大小为30

        Returns:
            str: random string generated
        """

        seeds = string.ascii_letters
        return ''.join(random.sample(seeds, size))

    @staticmethod
    def random_gen_address():
        """随机生成一个地址

        Returns:
            str: 北京市海淀区北三环中路xx号 - xx楼
        """
        street_num = random.randint(1, 99)
        building_num = random.randint(100, 99999)
        return f'北京市海淀区北三环中路{street_num}号 - {building_num}楼'

    @staticmethod
    def random_gen_fax():
        """随机生成一个传真号码

        Returns:
            str: 010-80xxxxxx
        """
        postfix = str(random.randint(100000, 999999))
        return f'010-80{postfix}'

    @staticmethod
    def random_gen_bank_name():
        """随机返回一个银行名称字符串

        Returns:
            str: 中国第xxx号银行
        """
        # todo: 爬虫获取国内有效的银行列表进行随机返回
        num = str(random.randint(100, 99999))
        return f'中国第{num}号银行'

    @staticmethod
    def gen_uuid():
        """返回一个基于时间戳的32个字符的uuid

        Returns:
            str: example => '6db8d55032f811ebadc5367dda197695'
        """
        return str(uuid.uuid1()).replace('-', '')

    @staticmethod
    def unique_sql_name() -> str:
        """
        Returns:
            str: example => ''hamster_31a531f6-6073-4c68-939f-6260bc4811f6''
        """
        return "hamster_" + str(uuid.uuid4()).lower()


if __name__ == '__main__':
    rando = MockDataUtil()
    print(rando.true_or_false())