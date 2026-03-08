const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());

app.get('/api/repo', (req, res) => {
  res.json({
    name: 'mock-repo',
    repoPath: '/mock/repo',
    indexedAt: new Date().toISOString(),
    stats: {}
  });
});

app.get('/api/graph', (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.write('{"nodes":[');
  for (let i = 0; i < 200000; i++) {
    if (i > 0) res.write(',');
    res.write(JSON.stringify({
      id: `node_${i}`,
      label: 'File',
      properties: {
        name: `file_${i}.js`,
        filePath: `/mock/repo/file_${i}.js`,
        content: 'mock content'
      }
    }));
  }
  res.write('],"relationships":[]}');
  res.end();
});

app.listen(3334, () => {
  console.log('Mock server running on port 3334');
});
