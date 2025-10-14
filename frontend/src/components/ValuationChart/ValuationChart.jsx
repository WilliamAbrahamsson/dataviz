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
      const newWidth = entries[0].contentRect.width
      setChartWidth(newWidth)
    })
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    if (!ref.current || !chartWidth) return
    const el = ref.current
    el.innerHTML = '' // clear previous svg

    // === dimensions ===
    const margin = { top: 16, right: 20, bottom: 28, left: 44 }
    const width = chartWidth
    const innerW = width - margin.left - margin.right
    const innerH = height - margin.top - margin.bottom

    // parse dates
    const parse = d3.timeParse('%Y-%m-%d')
    const series = data
      .map(d => ({ date: parse(d.date), value: +d.value }))
      .filter(d => d.date && !isNaN(d.value))

    // scales
    const x = d3.scaleUtc()
      .domain(d3.extent(series, d => d.date))
      .range([0, innerW])

    const y = d3.scaleLinear()
      .domain([0, d3.max(series, d => d.value) * 1.1 || 1])
      .nice()
      .range([innerH, 0])

    // svg
    const svg = d3.select(el)
      .append('svg')
      .attr('width', width)
      .attr('height', height)

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // grid
    g.append('g')
      .attr('class', 'grid y')
      .call(d3.axisLeft(y).ticks(5).tickSize(-innerW).tickFormat(''))
      .selectAll('line').attr('opacity', 0.15)

    // axes
    g.append('g')
      .attr('class', 'axis x')
      .attr('transform', `translate(0,${innerH})`)
      .call(d3.axisBottom(x).ticks(6).tickPadding(6))

    g.append('g')
      .attr('class', 'axis y')
      .call(d3.axisLeft(y).ticks(5).tickPadding(6))

    // line
    const line = d3.line()
      .x(d => x(d.date))
      .y(d => y(d.value))
      .curve(d3.curveMonotoneX)

    g.append('path')
      .datum(series)
      .attr('fill', 'none')
      .attr('stroke', '#457b9d')
      .attr('stroke-width', 2.5)
      .attr('d', line)

    // points
    g.selectAll('.pt')
      .data(series)
      .enter()
      .append('circle')
      .attr('class', 'pt')
      .attr('cx', d => x(d.date))
      .attr('cy', d => y(d.value))
      .attr('r', 3.5)
      .attr('fill', '#1d3557')

    // tooltip
    const tooltip = d3.select(el)
      .append('div')
      .attr('class', 'vc-tooltip')
      .style('opacity', 0)

    g.selectAll('.hit')
      .data(series)
      .enter()
      .append('circle')
      .attr('class', 'hit')
      .attr('cx', d => x(d.date))
      .attr('cy', d => y(d.value))
      .attr('r', 12)
      .attr('fill', 'transparent')
      .on('mouseenter', (_, d) => {
        tooltip
          .style('opacity', 1)
          .html(`<strong>€${d.value.toFixed(1)}M</strong><br>${d3.timeFormat('%b %Y')(d.date)}`)
      })
      .on('mousemove', (e) => {
        tooltip.style('left', `${e.offsetX + 16}px`).style('top', `${e.offsetY - 10}px`)
      })
      .on('mouseleave', () => tooltip.style('opacity', 0))
  }, [data, height, chartWidth])

  return <div className="valuation-chart" ref={ref} />
}
