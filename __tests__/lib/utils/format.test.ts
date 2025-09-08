import { formatDate, formatDateEnglish } from '../../../lib/utils/format'

describe('Format Utilities', () => {
  describe('formatDate', () => {
    it('应该格式化日期字符串为中文格式', () => {
      const result = formatDate('2024-01-15')
      expect(result).toContain('2024')
      expect(result).toContain('1')
      expect(result).toContain('15')
    })

    it('应该格式化Date对象为中文格式', () => {
      const date = new Date('2024-03-20')
      const result = formatDate(date)
      expect(result).toContain('2024')
      expect(result).toContain('3')
      expect(result).toContain('20')
    })

    it('应该处理不同的日期格式', () => {
      const result1 = formatDate('2024-12-25')
      const result2 = formatDate('2024/12/25')
      const result3 = formatDate('December 25, 2024')
      
      // 所有格式应该产生相同的结果
      expect(result1).toContain('2024')
      expect(result1).toContain('12')
      expect(result1).toContain('25')
      
      expect(result2).toEqual(result1)
      expect(result3).toEqual(result1)
    })

    it('应该处理无效日期', () => {
      const result = formatDate('invalid-date')
      expect(result).toBe('Invalid Date')
    })
  })

  describe('formatDateEnglish', () => {
    it('应该格式化日期字符串为英文格式', () => {
      const result = formatDateEnglish('2024-01-15')
      expect(result).toContain('January')
      expect(result).toContain('15')
      expect(result).toContain('2024')
    })

    it('应该格式化Date对象为英文格式', () => {
      const date = new Date('2024-03-20')
      const result = formatDateEnglish(date)
      expect(result).toContain('March')
      expect(result).toContain('20')
      expect(result).toContain('2024')
    })

    it('应该正确显示所有月份名称', () => {
      const months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
      ]
      
      months.forEach((month, index) => {
        const date = `2024-${String(index + 1).padStart(2, '0')}-15`
        const result = formatDateEnglish(date)
        expect(result).toContain(month)
      })
    })

    it('应该处理无效日期', () => {
      const result = formatDateEnglish('invalid-date')
      expect(result).toBe('Invalid Date')
    })

    it('应该产生不同于中文格式的结果', () => {
      const date = '2024-06-15'
      const chineseFormat = formatDate(date)
      const englishFormat = formatDateEnglish(date)
      
      expect(chineseFormat).not.toEqual(englishFormat)
      expect(englishFormat).toContain('June')
    })
  })
})