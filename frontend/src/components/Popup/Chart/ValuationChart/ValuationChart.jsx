import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import './ValuationChart.css'

export default function ValuationChart({
  data = [],
  height = 260,
  defaultPrediction,
  customPrediction,
}) {
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

    const parsedDefault = defaultPrediction == null ? NaN : Number(defaultPrediction)
    const parsedCustom = customPrediction == null ? NaN : Number(customPrediction)
    const hasDefault = Number.isFinite(parsedDefault)
    const hasCustom = Number.isFinite(parsedCustom)

    const x = d3.scaleUtc()
      .domain(d3.extent(series, (d) => d.date))
      .range([0, innerW])

    const baseMin = d3.min(series, (d) => d.value)
    const baseMax = d3.max(series, (d) => d.value) || 1
    const last = series[series.length - 1]
    const prevPoint = series.length >= 2 ? series[series.length - 2] : null

    const customPoint = hasCustom && last ? { date: last.date, value: parsedCustom } : null
    const defaultPoint = hasDefault && last ? { date: last.date, value: parsedDefault } : null

    let minVal = baseMin != null ? baseMin : 0
    let maxVal = baseMax

    if (customPoint) {
      minVal = Math.min(minVal, customPoint.value)
      maxVal = Math.max(maxVal, customPoint.value)
    }

    if (defaultPoint) {
      minVal = Math.min(minVal, defaultPoint.value)
      maxVal = Math.max(maxVal, defaultPoint.value)
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

    const addPrediction = (point, color, label, yOffset, classSuffix) => {
      if (!point) return

      if (prevPoint) {
        const startPoint = prevPoint
        const line = d3.line()
          .x((d) => x(d.date))
          .y((d) => y(d.value))

        const xTarget = x(point.date)
        const yTarget = y(point.value)
        const midX = (x(startPoint.date) + xTarget) / 2
        const midY = (y(startPoint.value) + yTarget) / 2
        const angle = (Math.atan2(yTarget - y(startPoint.value), xTarget - x(startPoint.date)) * 180) / Math.PI
        const labelX = midX
        const labelY = midY + yOffset

        g.append('path')
          .datum([startPoint, point])
          .attr('fill', 'none')
          .attr('stroke', color)
          .attr('stroke-width', 2.5)
          .attr('d', line)

        g.append('text')
          .attr('x', labelX)
          .attr('y', labelY)
          .attr('fill', color)
          .attr('font-size', 11)
          .attr('text-anchor', 'middle')
          .attr('class', `alt-label alt-label-${classSuffix}`)
          .attr('transform', `rotate(${angle}, ${midX}, ${midY})`)
          .text(label)
      }

      const xTarget = x(point.date)
      const yTarget = y(point.value)

      g.append('circle')
        .attr('class', `pt alt alt-${classSuffix}`)
        .attr('cx', xTarget)
        .attr('cy', yTarget)
        .attr('r', 3.5)
        .attr('fill', color)

      g.append('circle')
        .attr('class', `axis-marker axis-marker-${classSuffix}`)
        .attr('cx', 0)
        .attr('cy', y(point.value))
        .attr('r', 3)
        .attr('fill', color)
    }

    addPrediction(customPoint, '#2ecc71', 'Custom Prediction', -16, 'custom')
    addPrediction(defaultPoint, '#f39c12', 'Default Prediction', 16, 'default')

    const tooltip = d3.select(el).append('div')
      .attr('class', 'vc-tooltip').style('opacity', 0)

    const hitSeries = [
      ...series,
      ...(customPoint ? [customPoint] : []),
      ...(defaultPoint ? [defaultPoint] : []),
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
  }, [data, height, chartWidth, defaultPrediction, customPrediction])

  return <div className="valuation-chart" ref={ref} />
}
