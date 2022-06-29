# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 17:40:14 2022

@author: neo
"""

import unittest

from app import app,db,Movie,User,forge,initdb

class WatchlistTestCase(unittest.TestCase):
    def setUp(self):
        # 更新配置
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )
        
        #创建数据库和表
        db.create_all()
        
        #创建测试数据，一个用户，一个电影条目
        user=User(name='Test',username='test')
        user.set_password('123')
        movie=Movie(title='Test Movie Title',year='2019')
        db.session.add_all([user,movie])
        db.session.commit()
        
        self.client=app.test_client()
        self.runner=app.test_cli_runner()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    # 测试程序实例是否存在
    def test_app_exist(self):
        self.assertIsNone(app)
    
    # 测试程序是否处于测试模式
    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])
    
    # 测试 404 页面
    def test_404_page(self):
        response=self.client.get('/nothing')
        data=response.get_data(as_text=True)
        self.assertIn("Page Not Found - 404",data)
        self.assertIn("Go Back",data)
        self.assertEqual(response.status_code,404)
        
    # 测试主页
    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn("Test\'s Watchlist", data)
        self.assertIn("Test Movie Title", data)
        self.assertEqual(response.status_code, 200)
    
    # 辅助方法，用于登入用户
    def login(self):
        self.client.post('/login',data=dict(
            username='test',
            password='123'
        ),follow_redirects=True)
        
    # 测试创建条目
    def test_create_item(self):
        self.login()
        
        response=self.client.post('/',data=dict(
            title='New Movie',
            year='2019'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created.',data)
        self.assertIn('New Movie', data)
    
        # 测试创建条目,但电影标题为空
        response=self.client.post('/',data=dict(
            title='',
            year='2019'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created.',data)
        self.assertIn('Invalid input', data)
        
        # 测试创建条目,但电影年份为空
        response=self.client.post('/',data=dict(
            title='New Movie',
            year=''
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created.',data)
        self.assertIn('Invalid input', data)
    
    # 测试更新条目
    def test_update_item(self):
        self.login()
        # 测试更新页面
        response=self.client.get('/movie/edit/1')
        data=response.get_data(as_text=True)
        self.assertIn('Edit item',data)
        self.assertIn('Test Movie Title', data)
        self.assertIn('2019', data)
        # 测试更新条目操作
        response=self.client.post('/',data=dict(
            title='New Movie Edited',
            year='2019'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated.',data)
        self.assertIn('New Movie Editied', data)
        
        response=self.client.post('/',data=dict(
            title='',
            year='2019'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated.',data)
        self.assertIn('Invalid input.', data)
        
        response=self.client.post('/',data=dict(
            title='New Movie Edited Again',
            year=''
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated.',data)
        self.assertIn('New Movie Edited Again',data)
        self.assertIn('Invalid input.', data)
        
        def test_delete_item(self):
            self.login()
            response=self.client.post('/movie/delete/1',follow_redirects=True)
            data=response.get_data(as_text=True)
            self.assertIn('Item deleted.',data)
            self.assertNotIn('Test Movie Title', data)
        
        def test_login_protect(self):
            response=self.client.get('/')
            data=response.get_data(as_text=True)
            self.assertNotIn('Logout', data)
            self.assertNotIn('Settings', data)
            self.assertNotIn('<form method="post">', data)
            self.assertNotIn('Delete', data)
            self.assertNotIn('Edit', data)
        
        def test_login(self):
            response=self.client.post('/login',data=dict(
                username='test',
                password='123'
            ),follow_redirects=True)
            data=response.get_data(as_text=True)
            self.assertIn('Login success.',data)
            self.assertIn('Logout',data)
            self.assertIn('Settings',data)
            self.assertIn('Delete',data)
            self.assertIn('Edit',data)
            self.assertIn('<form method="post">',data)
            
            response=self.client.post('/login',data=dict(
                username='test',
                password='456'
            ),follow_redirects=True)
            data=response.get_data(as_text=True)
            self.assertNotIn('Login success.',data)
            self.assertIn('Invalid username or password.',data)
            
            response=self.client.post('/login',data=dict(
                username='wrong',
                password='123'
            ),follow_redirects=True)
            data=response.get_data(as_text=True)
            self.assertNotIn('Login success.',data)
            self.assertIn('Invalid input.',data)
            
            response=self.client.post('/login',data=dict(
                username='',
                password='123'
            ),follow_redirects=True)
            data=response.get_data(as_text=True)
            self.assertNotIn('Login success.',data)
            self.assertIn('Invalid input.',data)
            
            response=self.client.post('/login',data=dict(
                username='test',
                password=''
            ),follow_redirects=True)
            data=response.get_data(as_text=True)
            self.assertNotIn('Login success.',data)
            self.assertIn('Invalid input.',data)
            
        def test_logout(self):
            self.login()
            response=self.client.get('/logout',follow_redirects=True)
            data=response.get_data(as_text=True)
            self.assertIn('Goodbye.',data)
            self.assertNotIn('Logout',data)
            self.assertNotIn('Settings',data)
            self.assertNotIn('Delete',data)
            self.assertNotIn('Edit',data)
            self.assertNotIn('<form method="post">',data)
            
        def test_settings(self):
            self.login()
            response=self.client.get('/settings')
            data=response.get_data(as_text=True)
            self.assertIn('Settings',data)
            self.assertIn('Your Name',data)
            
            response=self.client.post('/settings',data=dict(
                name="Neo ni",
            ),follow_redirects=True)
            data=response.get_data(as_text=True)
            self.assertIn('Settings updated',data)
            self.assertIn('Neo ni',data)
            
            response=self.client.post('/settings',data=dict(
                name="",
            ),follow_redirects=True)
            data=response.get_data(as_text=True)
            self.assertNotIn('Settings updated',data)
            self.assertIn('Invalid input',data)
        
        def test_forge_command(self):
            result=self.runner.invoke(forge)
            self.assertIn('Done.',result.output)
            self.assertNotEqual(Movie.query.count(),0)
        
        def test_initdb_command(self):
            result=self.runner.invoke(initdb)
            self.assertIn('Initialized database.',result.output)
            
            
        def test_admin_command(self):
            db.drop_all()
            db.create_all()
            result=self.runner.invoke(arges=[
                'admin','--username','nll_011','--password','123456'    
            ])
            self.assertIn('Creating User...',result.output)
            self.assertIn('Done.',result.output)
            self.assertEqual(User.query.count(),1)
            self.assertEqual(User.query.first().username,'nll_011')
            self.assertTrue(User.query.first().validate_password('123456'))
            
            
        def test_admin_command_update(self):
            result=self.runner.invoke(args=[
                'admin','--username','nll_012','--password','234567'   
            ])
            self.assertIn('Updating User...',result.output)
            self.assertIn('Done.',result.output)
            self.assertEqual(User.query.count(),1)
            self.assertEqual(User.query.first().username,'nll_012')
            self.assertTrue(User.query.first().validate_password('234567'))
            
if __name__=='__main__':
    unittest.main()