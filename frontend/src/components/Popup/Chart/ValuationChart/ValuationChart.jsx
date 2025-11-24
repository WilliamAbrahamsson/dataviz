import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import './ValuationChart.css'

export default function ValuationChart({ data = [], height = 260 }) {
  const ref = useRef(null)
  const [chartWidth, setChartWidth] = useState(null)

  useEffect(() => {
    if (!ref.current) return
    const el = ref.current
    const observer = new ResizeObserver((entries) => {
      setChartWidth(entries[0].contentRect.width)
    })
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    if (!ref.current || !chartWidth) return
    const el = ref.current
    el.innerHTML = ''

    const margin = { top: 16, right: 20, bottom: 28, left: 44 }
    const width = chartWidth
    const innerW = width - margin.left - margin.right
    const innerH = height - margin.top - margin.bottom

    const parse = d3.timeParse('%Y-%m-%d')
    const series = data
      .map((d) => ({ date: parse(d.date), value: +d.value }))
      .filter((d) => d.date && !isNaN(d.value))

    if (!series.length) {
      return
    }

    const x = d3.scaleUtc()
      .domain(d3.extent(series, (d) => d.date))
      .range([0, innerW])

    const baseMin = d3.min(series, (d) => d.value)
    const baseMax = d3.max(series, (d) => d.value) || 1
    let altPoint = null
    let altPoint2 = null
    let prevPoint = null
    let minVal = baseMin != null ? baseMin : 0
    let maxVal = baseMax

    if (series.length >= 2) {
      const last = series[series.length - 1]
      const prev = series[series.length - 2]
      prevPoint = prev
      altPoint = {
        date: last.date,
        value: last.value * 1.1,
      }
      altPoint2 = {
        date: last.date,
        value: last.value * 0.9,
      }
      maxVal = Math.max(baseMax, altPoint.value, altPoint2.value)
      minVal = Math.min(minVal, altPoint.value, altPoint2.value)
    }

    const padding = (maxVal - minVal) * 0.1 || maxVal * 0.1 || 1

    const y = d3.scaleLinear()
      .domain([minVal - padding, maxVal + padding]).nice()
      .range([innerH, 0])

    const svg = d3.select(el).append('svg')
      .attr('width', width)
      .attr('height', height)

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

    g.append('g').attr('class', 'axis x')
      .attr('transform', `translate(0,${innerH})`)
      .call(d3.axisBottom(x).ticks(6).tickPadding(6))

    g.append('g').attr('class', 'axis y')
      .call(d3.axisLeft(y).ticks(5).tickPadding(6))

    const line = d3.line()
      .x((d) => x(d.date))
      .y((d) => y(d.value))

    g.append('path')
      .datum(series)
      .attr('fill', 'none')
      .attr('stroke', 'var(--accent)')
      .attr('stroke-width', 2.5)
      .attr('d', line)

    g.selectAll('.pt')
      .data(series)
      .enter()
      .append('circle')
      .attr('class', 'pt')
      .attr('cx', (d) => x(d.date))
      .attr('cy', (d) => y(d.value))
      .attr('r', 3.5)
      .attr('fill', 'var(--accent)')

    if (altPoint && prevPoint) {
      const altLine = d3.line()
        .x((d) => x(d.date))
        .y((d) => y(d.value))

      const x1 = x(prevPoint.date)
      const y1 = y(prevPoint.value)
      const x2 = x(altPoint.date)
      const y2 = y(altPoint.value)
      const midX = (x1 + x2) / 2
      const midY = (y1 + y2) / 2
      const angle = (Math.atan2(y2 - y1, x2 - x1) * 180) / Math.PI
      const labelX = midX
      const labelY = midY - 16

      g.append('path')
        .datum([prevPoint, altPoint])
        .attr('fill', 'none')
        .attr('stroke', '#2ecc71')
        .attr('stroke-width', 2.5)
        .attr('d', altLine)

      g.append('circle')
        .attr('class', 'pt alt')
        .attr('cx', x2)
        .attr('cy', y2)
        .attr('r', 3.5)
        .attr('fill', '#2ecc71')

      g.append('circle')
        .attr('class', 'axis-marker axis-marker-default')
        .attr('cx', 0)
        .attr('cy', y(altPoint.value))
        .attr('r', 3)
        .attr('fill', '#2ecc71')

      g.append('text')
        .attr('x', labelX)
        .attr('y', labelY)
        .attr('fill', '#2ecc71')
        .attr('font-size', 11)
        .attr('text-anchor', 'middle')
        .attr('class', 'alt-label alt-label-default')
        .attr('transform', `rotate(${angle}, ${midX}, ${midY})`)
        .text('Modified Prediction')
    }

    if (altPoint2 && prevPoint) {
      const altLine2 = d3.line()
        .x((d) => x(d.date))
        .y((d) => y(d.value))

      const x1b = x(prevPoint.date)
      const y1b = y(prevPoint.value)
      const x2b = x(altPoint2.date)
      const y2b = y(altPoint2.value)
      const midX2 = (x1b + x2b) / 2
      const midY2 = (y1b + y2b) / 2
      const angle2 = (Math.atan2(y2b - y1b, x2b - x1b) * 180) / Math.PI
      const labelX2 = midX2
      const labelY2 = midY2 + 16

      g.append('path')
        .datum([prevPoint, altPoint2])
        .attr('fill', 'none')
        .attr('stroke', '#f39c12')
        .attr('stroke-width', 2.5)
        .attr('d', altLine2)

      g.append('circle')
        .attr('class', 'pt alt alt-2')
        .attr('cx', x2b)
        .attr('cy', y2b)
        .attr('r', 3.5)
        .attr('fill', '#f39c12')

      g.append('circle')
        .attr('class', 'axis-marker axis-marker-modified')
        .attr('cx', 0)
        .attr('cy', y(altPoint2.value))
        .attr('r', 3)
        .attr('fill', '#f39c12')

      g.append('text')
        .attr('x', labelX2)
        .attr('y', labelY2)
        .attr('fill', '#f39c12')
        .attr('font-size', 11)
        .attr('text-anchor', 'middle')
        .attr('class', 'alt-label alt-label-modified')
        .attr('transform', `rotate(${angle2}, ${midX2}, ${midY2})`)
        .text('Default Prediction')
    }

    const tooltip = d3.select(el).append('div')
      .attr('class', 'vc-tooltip').style('opacity', 0)

    const hitSeries = [
      ...series,
      ...(altPoint ? [altPoint] : []),
      ...(altPoint2 ? [altPoint2] : []),
    ]

    if (series.length) {
      const latest = series[series.length - 1]
      g.append('circle')
        .attr('class', 'axis-marker axis-marker-latest')
        .attr('cx', 0)
        .attr('cy', y(latest.value))
        .attr('r', 3)
        .attr('fill', 'var(--accent)')
    }

    g.selectAll('.hit')
      .data(hitSeries)
      .enter().append('circle')
      .attr('class', 'hit')
      .attr('cx', (d) => x(d.date))
      .attr('cy', (d) => y(d.value))
      .attr('r', 12).attr('fill', 'transparent')
      .on('mouseenter', (_, d) => {
        tooltip.style('opacity', 1)
          .html(`<strong>€${d.value.toFixed(1)}M</strong><br>${d3.timeFormat('%b %Y')(d.date)}`)
      })
      .on('mousemove', (e) => {
        tooltip.style('left', `${e.offsetX + 16}px`).style('top', `${e.offsetY - 10}px`)
      })
      .on('mouseleave', () => tooltip.style('opacity', 0))
  }, [data, height, chartWidth])

  return <div className="valuation-chart" ref={ref} />
}
