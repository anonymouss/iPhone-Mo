# iPhone Macau Monitor

Ref: https://github.com/codcodog/iphone-spider

- Monitor status of iPhone available for pre-order in apple.com/mo.
- Notify the receivers (defined in `config.py`) by WeChat once available.
- And open the reservation page automatically for the most desired model (Ranked in `config.py`).

> Note: To save operation time and increase booking success rate. Please login your apple-id in advance(in apple.com/mo). And please send SMS to `85366016382` as well in advance to obtain the registration code for your reservation(The code seems to be valid for 30 minutes).

## Usage

```bash
# 1. install python3
# 2. pip3 install -r requirements.txt
# 3. py -3 main.py

# NOTE: wxpy/itchat was blocked by Tencent now. Hence not every WeChat user can use it
```
