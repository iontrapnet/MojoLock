--[[
print('lua')

local py = python.eval
local enum = python.enumerate
local iter = python.iter

function Window_setState(self, state)
    self.output()
    if (state == 1) then
        self.plot.resetGrid(1, 1)
        self.views = py('[(0, 0, 0, 0, 4)]')
        self.view.setItems(py("['']"))
        self.dds0.setValue(32, 2, 0)
        self.dds1.setValue(51200, 2, 0)
        self.setFilterParam(9)
        self.plot.rects[py('(0, 0)')].xy = true
    end
    --[-[elif state == 4:
        self.plot.resetGrid(1, 1)
        self.views = [(0, 0, 6, 6, 7)]
        self.view.setItems(['Lamp'])
        self.dds1.setValue(32, 2, 0)
    elif state == 5:
        self.plot.resetGrid(1, 1)
        self.views = [(0, 0, 6, 1, 5)]
        self.view.setItems(['Cavity'])
        self.dds0.setValue(30000, 2, 0)
        self.dds1.setValue(32, 2, 0)
        self.setFilterParam(9)
    elif state == 8:
        self.plot.resetGrid(1, 2)
        self.views = [(0, 0, 6, 4, 5), (0, 1, 6, 8, 8)]
        self.view.setItems(['Cavity', 'Lamp'])]-]
end

function MinMax(arr)
    mink = -1
    minv = tonumber('inf')
    maxk = -1
    maxv = tonumber('-inf')
    for k, v in enum(arr) do
        if v < minv then
            mink = k
            minv = v
        end
        if v > maxv then
            maxk = k
            maxv = v
        end
    end
    return mink, minv, maxk, maxv
end

function PlotCtrl_setData(self, row, col, x, y)
    print(row, col)
    print(MinMax(y))
end

function Window_doRun(self)
    print('hehe')
end

function Window_doTimeout(self)
    --local ret = window.input('hehe', 'haha', '')
    --if (not ret[1]) then window.close() end
    --print(ret[1])
    --window.output(ret[0], ret[1], self.mixer_offset.value(), self.filter_param.value())
end
]]