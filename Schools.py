"""
教育部公布具有招生资格的高校名单。
根据教育部公布的名单，截至2019年6月15日，全国高等学校共计2956所，
其中：普通高等学校2688所(含独立学院257所)，成人高等学校268所。
"""
import requests,pymysql.cursors
from lxml import etree
from pyecharts.charts import Bar
from pyecharts import options as opts

# 获取各省份学校URL
def Provinces():
	global headers,city_name
	url_eol = 'https://daxue.eol.cn/mingdan.shtml'
	headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362'
	}
	response = requests.get(url_eol,headers=headers)
	response.encoding = 'utf-8'
	html = etree.HTML(response.text)
	city_name = html.xpath("//div[@class='province']/a/text()")#
	city_urls = html.xpath("//div[@class='province']/a/@href")
	# print("总省份数：",len(city_urls))
	return city_urls

# 获取学校名单及相关信息
def Schools():
	global province
	mingdan = []
	province = []
	for url in Provinces():
		res = requests.get(url,headers=headers)
		res.encoding = 'utf-8'
		html = etree.HTML(res.text,parser=etree.HTMLPullParser(encoding='utf-8'))
		lines = html.xpath("//div[@class='tablebox']/table/tbody/tr")[2:]
		province.append(len(lines))
		for line in lines:
			lable = line.xpath("td[1]/text()")[0]
			school = line.xpath("td[2]/text()")[0]
			code = line.xpath("td[3]/text()")[0]
			deparment = line.xpath("td[4]/text()")[0]
			location = line.xpath("td[5]/text()")[0]
			level = line.xpath("td[6]/text()")[0]
			if line.xpath("td[7]/text()") != ['民办']:
				note = '公办'
			else:
				note = '民办'
			mingdan.append((lable,school,code,deparment,location,level,note))
	return mingdan

# 把数据写入数据库
def Database():
	connect = pymysql.connect(
		db='Schools',
		host='localhost',
		port=3306,
		password='242359',
		user='root',
		charset='utf8'
	)
	cursor = connect.cursor()
	cursor.execute("""truncate table mingdan""")
	connect.commit()
	sql = """insert into mingdan(lable,school,code,deparment,location,level,note)
	values("%s","%s","%s","%s","%s","%s","%s")"""
	for info in Schools():
		data = (info[0],info[1],info[2],info[3],info[4],info[5],info[6])
		cursor.execute(sql % data)
	connect.commit()
	connect.close()

# 各省学校数量的可视化
def school_View():
	bar = Bar()
	bar.add_xaxis(city_name)

	bar.add_yaxis('各省份学校数量的柱状图',province)
	bar.set_global_opts(title_opts=opts.TitleOpts(title="全国具有招生资格的高校名单",subtitle="此数据经由教育部统计"))
	bar.render()

def main():
	Schools()
	Database()
	school_View()

if __name__ == '__main__':
	main()
