

从以前的selenium规范，变成现在可以调用的selenium脚本
1. 将非环境的导包设置成绝对路径
2. 将各级目录全部设置为python文件夹
3.更改数据流出入口（还未完成），json来源变成start函数的接受参数，
   我会传入一个
[     {'email': 'meenranvno@mail.ru', 'password': 'vJC5YxDBdqSrgF7DHmNS',
     'website': 'https://heydaraliyevcenterganja.com',
     'description': 'Harmonizing Architecture, Culture, and History: A Unique Blend of Heritage.',
      'firstname': 'DAEaGnDAbV', 
     'lastname': 'IKicTbcYEW'
   },
     {'email': 'meenranvno@mail.ru', 'password': 'vJC5YxDBdqSrgF7DHmNS',
     'website': 'https://heydaraliyevcenterganja.com',
     'description': 'Harmonizing Architecture, Culture, and History: A Unique Blend of Heritage.',
      'firstname': 'DAEaGnDAbV', 
     'lastname': 'IKicTbcYEW'
   },
   ....................
   ]
   
类似的数据流
   
4.根据传入的数据流修改数据变量