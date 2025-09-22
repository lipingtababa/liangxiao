/**
 * Cucumber 配置文件
 * 用于配置 BDD 验收测试
 */

module.exports = {
  default: {
    paths: ['features/**/*.feature'],
    require: ['features/step_definitions/**/*.js'],
    format: [
      '@cucumber/pretty-formatter',
      'html:test-results/cucumber-report.html',
      'json:test-results/cucumber-report.json',
      'progress-bar'
    ],
    parallel: 2,
    retry: 1,
    retryTagFilter: '@flaky',
    tags: 'not @wip and not @manual',
    publishQuiet: true
  },
  ci: {
    paths: ['features/**/*.feature'],
    require: ['features/step_definitions/**/*.js'],
    format: [
      'json:test-results/cucumber-report.json',
      'progress'
    ],
    parallel: 4,
    retry: 2,
    tags: 'not @wip and not @manual',
    publishQuiet: true
  }
};