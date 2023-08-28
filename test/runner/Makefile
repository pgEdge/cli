CXXFLAGS = -g -O0
LDFLAGS  = -g

runner:	runner.o
	$(CXX) $(CXXFLAGS) -o $@ $^

runner.o: runner.cpp 

clean:
	rm -f runner.o runner
