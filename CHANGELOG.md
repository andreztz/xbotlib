# xbotlib x.x.x (UNRELEASED)

# xbotlib 0.14.0 (2021-01-19)

- Reduce generated config flow to only mandatory options
- Fix support for multiple rooms in configuration file ([#33](https://git.autonomic.zone/decentral1se/xbotlib/issues/33))

# xbotlib 0.13.1 (2021-01-19)

- Document `Bot` attributes/functions ([#35](https://git.autonomic.zone/decentral1se/xbotlib/issues/35))
- Provide a `Bot.respond` function ([#34](https://git.autonomic.zone/decentral1se/xbotlib/issues/34))

# xbotlib 0.13.0 (2021-01-18)

- Allow commands to be detected in all parts of the message

# xbotlib 0.12.4 (2021-01-18)

- Allow `Bot.group` to respond to file uploads ([#32](https://git.autonomic.zone/decentral1se/xbotlib/issues/32))

# xbotlib 0.12.3 (2021-01-17)

- Support OOB URLs in `SimpleMessage`

# xbotlib 0.12.2 (2021-01-17)

- Support loading Jinja2 template ([#30](https://git.autonomic.zone/decentral1se/xbotlib/issues/30))

# xbotlib 0.12.1 (2021-01-17)

- Allow to configure port

# xbotlib 0.12.0 (2021-01-17)

- Support running a web server ([#22](https://git.autonomic.zone/decentral1se/xbotlib/issues/22))
- Remove bots from core now that things are stabilising ([#29](https://git.autonomic.zone/decentral1se/xbotlib/issues/29))

# xbotlib 0.11.0 (2021-01-16)

- Allow to configure avatar from configuration file and environment
- Load Redis details fron conf and CLI also ([#23](https://git.autonomic.zone/decentral1se/xbotlib/issues/23))
- Migrate Redis environment naming: `REDIS_URL` -> `XBOT_REDIS_URL` ([#23](https://git.autonomic.zone/decentral1se/xbotlib/issues/23))
- Allow to load custom plugins ([#24](https://git.autonomic.zone/decentral1se/xbotlib/issues/24))
- Supports rooms configuration for auto-joining ([#25](https://git.autonomic.zone/decentral1se/xbotlib/issues/25))
- Add `--no-auto-join` to disable automatically responding to invites ([#26](https://git.autonomic.zone/decentral1se/xbotlib/issues/26))
- Improve UX for initial configuration generation

# xbotlib 0.10.0 (2021-01-16)

- Implement Redis based storage ([#21](https://git.autonomic.zone/decentral1se/xbotlib/issues/21))
- Add `GlossBot` ([#10](https://git.autonomic.zone/decentral1se/xbotlib/issues/10))
- Revise command syntax and use unified `@` approach
- `SimpleMessage.body` -> `SimpleMessage.text`
- Add `SimpleMessage.content` which simplifies parsing logic

# xbotlib 0.9.0 (2021-01-15)

- Re-worked `!bots` -> `/bots`

# xbotlib 0.8.2 (2021-01-15)

- Add `!bots` command to summon status

# xbotlib 0.8.1 (2021-01-15)

- Support avatars ([#17](https://git.autonomic.zone/decentral1se/xbotlib/issues/17))

# xbotlib 0.8.0 (2021-01-14)

- Support not providing response implementation ([#18](https://git.autonomic.zone/decentral1se/xbotlib/issues/18))
- Arrange precedence logic for config loading ([#14](https://git.autonomic.zone/decentral1se/xbotlib/issues/14))
- Remove `--no-input` option and detect it automatically ([#14](https://git.autonomic.zone/decentral1se/xbotlib/issues/14))
- Refer to `jid` as `account` from now on both internally and externally ([#14](https://git.autonomic.zone/decentral1se/xbotlib/issues/14))
- `bot.conf` -> `$name.conf` ([#3](https://git.autonomic.zone/decentral1se/xbotlib/issues/3))
- Support `!` style commands ([#12](https://git.autonomic.zone/decentral1se/xbotlib/issues/12))

# xbotlib 0.7.1 (2021-01-13)

- Support logging ([#2](https://git.autonomic.zone/decentral1se/xbotlib/issues/2))

# xbotlib 0.7.0 (2021-01-13)

- Remove `room` as configuration and support arbitrary invite acceptance ([#15](https://git.autonomic.zone/decentral1se/xbotlib/issues/15))

# xbotlib 0.6.0 (2021-01-13)

- Implement direct/group API ([#13](https://git.autonomic.zone/decentral1se/xbotlib/issues/13))

# xbotlib 0.5.0 (2021-01-13)

- Revert `source` -> `sender` on `SimpleMessage` as it is more clear ([cf93c07294](https://git.autonomic.zone/decentral1se/xbotlib/commit/cf93c07294d72b11d465491680f5befe882db9bf))

# xbotlib 0.4.0 (2021-01-13)

- Internally manage all example bots ([#11](https://git.autonomic.zone/decentral1se/xbotlib/issues/11))
- `EasyMessage` -> `SimpleMessage` ([1a88f7049b](https://git.autonomic.zone/decentral1se/xbotlib/commit/1a88f7049b2cc6b6bc76efbcbb6e281b1d1227ff))
- Change `sender` to `source` on `SimpleMessage` to reflect user/room behaviour ([e0c8583b2d](https://git.autonomic.zone/decentral1se/xbotlib/commit/e0c8583b2d592d5b6668fea1ba0d7b4ffcba5600))
- Make `EchoBot` support group chats ([1137624180](https://git.autonomic.zone/decentral1se/xbotlib/commit/11376241808c967a83d6587e9d9acd21e808c3cf))
- Add additional `room` attribute to `SimpleMessage` ([deca260a67](https://git.autonomic.zone/decentral1se/xbotlib/commit/deca260a6705c18fab899149cb1817c050dcada8))

# xbotlib 0.3.2 (2021-01-12)

- Fix config parser environment loading for missing optional variables ([f909d43c59](https://git.autonomic.zone/decentral1se/xbotlib/commit/f909d43c591c011c9baf8cb967777b744cb6b566))

# xbotlib 0.3.1 (2021-01-12)

- Support `--no-input` flag and read configuration from the environment ([4f6f102d1e](https://git.autonomic.zone/decentral1se/xbotlib/commit/4f6f102d1e46aa888e7b49e31c2706bb276ea182))

# xbotlib 0.3.0 (2021-01-10)

- Error out if you don't provide a `react` implementation ([eb87de7de5](https://git.autonomic.zone/decentral1se/xbotlib/commit/eb87de7de5422eb584a56f4266a2bf1eddc5513d))
- Change `reply` to accept `body` as the first argument ([bca6e6c90a](https://git.autonomic.zone/decentral1se/xbotlib/commit/bca6e6c90a295ea99101cd93960b290573627065))

# xbotlib 0.2.0 (2021-01-10)

- Refine API for direct/chat responses ([18bae6ec09](https://git.autonomic.zone/decentral1se/xbotlib/commit/18bae6ec09c417005a438ce829746231c95b9d67))

# xbotlib 0.1.0 (2021-01-10)

- Initial release
