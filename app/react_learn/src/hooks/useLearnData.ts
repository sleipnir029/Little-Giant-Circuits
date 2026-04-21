import { useState, useEffect } from 'react'
import type { Manifest, LearnPackage } from '../types'

interface LearnDataState {
  manifest: Manifest | null
  selectedPackage: LearnPackage | null
  loadingManifest: boolean
  loadingPackage: boolean
  manifestError: string | null
  packageError: string | null
  selectTask: (task: string, traceId: string) => void
}

export function useLearnData(): LearnDataState {
  const [manifest, setManifest] = useState<Manifest | null>(null)
  const [selectedPackage, setSelectedPackage] = useState<LearnPackage | null>(null)
  const [loadingManifest, setLoadingManifest] = useState(true)
  const [loadingPackage, setLoadingPackage] = useState(false)
  const [manifestError, setManifestError] = useState<string | null>(null)
  const [packageError, setPackageError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/learn_data/manifest.json')
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json() as Promise<Manifest>
      })
      .then((m) => {
        setManifest(m)
        setLoadingManifest(false)
        // auto-select induction as the canonical demo task
        const induction = m.packages.find((p) => p.task === 'induction') ?? m.packages[0]
        if (induction) loadPackage(induction.task, induction.trace_id)
      })
      .catch((e: Error) => {
        setManifestError(e.message)
        setLoadingManifest(false)
      })
  }, [])

  function loadPackage(task: string, traceId: string) {
    setLoadingPackage(true)
    setPackageError(null)
    fetch(`/learn_data/${task}/${traceId}.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json() as Promise<LearnPackage>
      })
      .then((pkg) => {
        setSelectedPackage(pkg)
        setLoadingPackage(false)
      })
      .catch((e: Error) => {
        setPackageError(e.message)
        setLoadingPackage(false)
      })
  }

  function selectTask(task: string, traceId: string) {
    loadPackage(task, traceId)
  }

  return {
    manifest,
    selectedPackage,
    loadingManifest,
    loadingPackage,
    manifestError,
    packageError,
    selectTask,
  }
}
