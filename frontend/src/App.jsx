import React, { useState, useEffect } from 'react';
import { 
  Container, Typography, TextField, Button, Card, CardContent, CardHeader,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Dialog, DialogTitle, DialogContent, DialogActions, Grid, Collapse, IconButton
} from '@mui/material';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:7070';
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const App = () => {
  const [events, setEvents] = useState([]);
  const [groupedEvents, setGroupedEvents] = useState({});
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  useEffect(() => {
    fetchEvents();
  }, []);

  useEffect(() => {
    const filtered = events.filter(event => 
      event.event_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      event.topic.toLowerCase().includes(searchTerm.toLowerCase()) ||
      event.status.toLowerCase().includes(searchTerm.toLowerCase())
    );
    const grouped = filtered.reduce((acc, event) => {
      if (!acc[event.event_id]) {
        acc[event.event_id] = [];
      }
      acc[event.event_id].push(event);
      return acc;
    }, {});
    setGroupedEvents(grouped);
  }, [searchTerm, events]);

  const fetchEvents = async () => {
    try {
      const response = await fetch(`${API_URL}/events`);
      const data = await response.json();
      setEvents(data);
    } catch (error) {
      console.error('Error fetching events:', error);
    }
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleEventClick = async (eventId) => {
    try {
      const response = await fetch(`${API_URL}/event/${eventId}`);
      const data = await response.json();
      setSelectedEvent(data[0]);
      setIsDialogOpen(true);
    } catch (error) {
      console.error('Error fetching event details:', error);
    }
  };

  const handleCloseDialog = () => {
    setIsDialogOpen(false);
  };

  const prepareLatencyData = () => {
    return events.map(event => ({
      id: event.event_id,
      latency: event.processing_time || Math.random() * 1000
    })).sort((a, b) => b.latency - a.latency).slice(0, 20);
  };

  const prepareErrorRateData = () => {
    const totalEvents = events.length;
    const errorEvents = events.filter(event => event.status === 'error').length;
    return [
      { name: 'Success', value: totalEvents - errorEvents },
      { name: 'Error', value: errorEvents }
    ];
  };

  const prepareTopErrorSourcesData = () => {
    const sourceCount = {};
    events.filter(event => event.status === 'error').forEach(event => {
      sourceCount[event.source] = (sourceCount[event.source] || 0) + 1;
    });
    return Object.entries(sourceCount)
      .map(([source, count]) => ({ source, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);
  };

  const EventGroup = ({ eventId, events }) => {
    const [open, setOpen] = useState(false);

    return (
      <>
        <TableRow>
          <TableCell>
            <IconButton size="small" onClick={() => setOpen(!open)}>
              {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
            </IconButton>
          </TableCell>
          <TableCell>{eventId}</TableCell>
          <TableCell>{events[0].topic}</TableCell>
          <TableCell>{events[0].status}</TableCell>
          <TableCell>
            <Button 
              variant="contained" 
              onClick={() => handleEventClick(eventId)}
            >
              View Details
            </Button>
          </TableCell>
        </TableRow>
        <TableRow>
          <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={5}>
            <Collapse in={open} timeout="auto" unmountOnExit>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Timestamp</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Source</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {events.map((event, index) => (
                    <TableRow key={index}>
                      <TableCell>{event.timestamp}</TableCell>
                      <TableCell>{event.status}</TableCell>
                      <TableCell>{event.source}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Collapse>
          </TableCell>
        </TableRow>
      </>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Event Monitoring Dashboard
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Top 20 Highest Latency Events" />
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={prepareLatencyData()} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="id" type="category" width={150} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="latency" fill="#82ca9d" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardHeader title="Error Rate" />
                <CardContent>
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={prepareErrorRateData()}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {prepareErrorRateData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12}>
              <Card>
                <CardHeader title="Top 5 Error Sources" />
                <CardContent>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={prepareTopErrorSourcesData()}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="source" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="count" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>
      </Grid>

      <TextField
        fullWidth
        label="Search events"
        variant="outlined"
        value={searchTerm}
        onChange={handleSearch}
        sx={{ mb: 4 }}
      />

      <Card>
        <CardHeader title="Event List" />
        <CardContent>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell />
                  <TableCell>Event ID</TableCell>
                  <TableCell>Topic</TableCell>
                  <TableCell>Latest Status</TableCell>
                  <TableCell>Action</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.entries(groupedEvents).map(([eventId, events]) => (
                  <EventGroup key={eventId} eventId={eventId} events={events} />
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      <Dialog open={isDialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Event Details</DialogTitle>
        <DialogContent>
          {selectedEvent && (
            <>
              <Typography><strong>Event ID:</strong> {selectedEvent.event_id}</Typography>
              <Typography><strong>Topic:</strong> {selectedEvent.topic}</Typography>
              <Typography><strong>Status:</strong> {selectedEvent.status}</Typography>
              <Typography><strong>Timestamp:</strong> {selectedEvent.timestamp}</Typography>
              <Typography><strong>Source:</strong> {selectedEvent.source}</Typography>
              <Typography><strong>Details:</strong> {selectedEvent.details || 'N/A'}</Typography>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default App;