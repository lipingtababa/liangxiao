# language: zh-CN
@smoke
功能: 冒烟测试
  作为系统管理员
  我希望验证基本功能正常工作
  以便确保系统可以正常运行

  场景: 验证测试环境
    假设 系统已经正确配置
    那么 文件 "package.json" 应该存在
    并且 文件 "cucumber.js" 应该存在

  场景: 验证目录结构
    假设 系统已经正确配置
    那么 文件应该保存在 "posts" 目录
    并且 文件应该保存在 "public/images" 目录
    并且 文件应该保存在 "scripts" 目录