function meetingApp() {
  return {
    // State
    selectedFile: null,
    processing: false,
    processingStatus: "Initializing...",
    processingProgress: 0,
    currentResult: null,
    allActions: [],
    actionStats: { total: 0, open: 0, completed: 0 },
    showActions: false,
    dragover: false,
    error: null,
    success: null,

    // Initialize
    init() {
      this.loadActions()
      this.loadActionStats()

      // Auto-hide toasts
      this.$watch("error", (value) => {
        if (value) setTimeout(() => (this.error = null), 5000)
      })
      this.$watch("success", (value) => {
        if (value) setTimeout(() => (this.success = null), 3000)
      })
    },

    // File handling
    handleFileDrop(event) {
      this.dragover = false
      const files = event.dataTransfer.files
      if (files.length > 0) {
        this.selectedFile = files[0]
        this.validateFile()
      }
    },

    handleFileSelect(event) {
      const files = event.target.files
      if (files.length > 0) {
        this.selectedFile = files[0]
        this.validateFile()
      }
    },

    validateFile() {
      const allowedTypes = ["audio/mpeg", "audio/wav", "audio/m4a", "video/mp4", "video/avi", "video/quicktime"]
      const allowedExtensions = [".mp3", ".wav", ".m4a", ".mp4", ".avi", ".mov"]

      const fileExtension = this.selectedFile.name.toLowerCase().substring(this.selectedFile.name.lastIndexOf("."))

      if (!allowedTypes.includes(this.selectedFile.type) && !allowedExtensions.includes(fileExtension)) {
        this.error = "Please select a valid audio or video file (MP3, WAV, M4A, MP4, AVI, MOV)"
        this.selectedFile = null
        return false
      }

      if (this.selectedFile.size > 500 * 1024 * 1024) {
        // 500MB limit
        this.error = "File size must be less than 500MB"
        this.selectedFile = null
        return false
      }

      return true
    },

    // File processing
    async processFile() {
      if (!this.selectedFile || !this.validateFile()) return

      this.processing = true
      this.processingProgress = 0
      this.currentResult = null

      try {
        const formData = new FormData()
        formData.append("file", this.selectedFile)

        // Simulate processing steps
        const steps = [
          "Uploading file...",
          "Converting audio format...",
          "Performing speech-to-text...",
          "Identifying speakers...",
          "Processing transcript...",
          "Generating summary...",
          "Detecting action items...",
          "Extracting assignees...",
          "Finalizing results...",
        ]

        let stepIndex = 0
        const progressInterval = setInterval(() => {
          if (stepIndex < steps.length) {
            this.processingStatus = steps[stepIndex]
            this.processingProgress = ((stepIndex + 1) / steps.length) * 90
            stepIndex++
          }
        }, 1000)

        const response = await fetch("/api/upload", {
          method: "POST",
          body: formData,
        })

        clearInterval(progressInterval)

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || "Processing failed")
        }

        this.processingProgress = 100
        this.processingStatus = "Complete!"

        const result = await response.json()
        this.currentResult = result
        this.success = "Meeting processed successfully!"

        // Refresh actions to include new ones
        await this.loadActions()
        await this.loadActionStats()
      } catch (error) {
        console.error("Processing error:", error)
        this.error = error.message || "Failed to process meeting file"
      } finally {
        setTimeout(() => {
          this.processing = false
          this.processingStatus = "Initializing..."
          this.processingProgress = 0
        }, 1000)
      }
    },

    // Actions management
    async loadActions() {
      try {
        const response = await fetch("/api/actions")
        if (response.ok) {
          const data = await response.json()
          this.allActions = data.actions || []
        }
      } catch (error) {
        console.error("Failed to load actions:", error)
      }
    },

    async loadActionStats() {
      try {
        const stats = { total: 0, open: 0, completed: 0 }

        this.allActions.forEach((action) => {
          stats.total++
          if (action.status === "open") stats.open++
          if (action.status === "completed") stats.completed++
        })

        this.actionStats = stats
      } catch (error) {
        console.error("Failed to load action stats:", error)
      }
    },

    async markActionComplete(actionId) {
      try {
        const response = await fetch(`/api/actions/${actionId}/complete`, {
          method: "POST",
        })

        if (response.ok) {
          this.success = "Action marked as completed!"
          await this.loadActions()
          await this.loadActionStats()
        } else {
          throw new Error("Failed to update action")
        }
      } catch (error) {
        this.error = error.message || "Failed to update action"
      }
    },

    async refreshActions() {
      await this.loadActions()
      await this.loadActionStats()
      this.success = "Actions refreshed!"
    },

    // Export functions
    async exportPDF() {
      if (!this.currentResult) return

      try {
        const response = await fetch(`/api/export/${this.currentResult.filename}`)
        if (response.ok) {
          const blob = await response.blob()
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement("a")
          a.href = url
          a.download = `${this.currentResult.filename}_minutes.pdf`
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          window.URL.revokeObjectURL(url)
          this.success = "PDF exported successfully!"
        } else {
          throw new Error("Export failed")
        }
      } catch (error) {
        this.error = "Failed to export PDF"
      }
    },

    exportJSON() {
      if (!this.currentResult) return

      const dataStr = JSON.stringify(this.currentResult, null, 2)
      const dataBlob = new Blob([dataStr], { type: "application/json" })
      const url = window.URL.createObjectURL(dataBlob)
      const a = document.createElement("a")
      a.href = url
      a.download = `${this.currentResult.filename}_minutes.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      this.success = "JSON exported successfully!"
    },

    // Utility functions
    formatFileSize(bytes) {
      if (!bytes) return "0 Bytes"
      const k = 1024
      const sizes = ["Bytes", "KB", "MB", "GB"]
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
    },

    formatDate(dateString) {
      if (!dateString) return ""
      return new Date(dateString).toLocaleDateString()
    },

    getUrgencyClass(urgency) {
      const classes = {
        urgent: "bg-red-100 text-red-800",
        high: "bg-orange-100 text-orange-800",
        medium: "bg-yellow-100 text-yellow-800",
        low: "bg-green-100 text-green-800",
      }
      return classes[urgency] || "bg-gray-100 text-gray-800"
    },

    getStatusClass(status) {
      const classes = {
        open: "bg-blue-100 text-blue-800",
        completed: "bg-green-100 text-green-800",
        overdue: "bg-red-100 text-red-800",
      }
      return classes[status] || "bg-gray-100 text-gray-800"
    },
  }
}
